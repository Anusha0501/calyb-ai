"""Small custom adjacency-list graph with JSON and GraphML export."""
from __future__ import annotations
import html, json
from collections import deque
from pathlib import Path
from src.models.edge import Edge
from src.models.node import Node

class KnowledgeGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.adjacency: dict[str, set[str]] = {}
        self._edge_keys: set[tuple[str, str, str, str]] = set()

    def add_node(self, node: Node) -> None:
        self.nodes.setdefault(node.id, node)
        self.adjacency.setdefault(node.id, set())

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self.nodes:
            self.add_node(Node(edge.source, "External", edge.source, {}))
        if edge.target not in self.nodes:
            self.add_node(Node(edge.target, "External", edge.target, {}))
        key = (edge.source, edge.target, edge.type, edge.evidence.sentence)
        if key not in self._edge_keys:
            self._edge_keys.add(key)
            self.edges.append(edge)
            self.adjacency.setdefault(edge.source, set()).add(edge.target)
            self.adjacency.setdefault(edge.target, set()).add(edge.source)

    def neighbors(self, node_id: str) -> list[str]:
        return sorted(self.adjacency.get(node_id, set()))

    def related_nodes(self, node_id: str, max_depth: int = 2) -> list[str]:
        seen = {node_id}
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        related: list[str] = []
        while queue:
            current, depth = queue.popleft()
            if depth == max_depth:
                continue
            for neighbor in self.neighbors(current):
                if neighbor not in seen:
                    seen.add(neighbor)
                    related.append(neighbor)
                    queue.append((neighbor, depth + 1))
        return related

    def shortest_path(self, source: str, target: str) -> list[str]:
        if source == target:
            return [source]
        queue: deque[list[str]] = deque([[source]])
        seen = {source}
        while queue:
            path = queue.popleft()
            for neighbor in self.neighbors(path[-1]):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def export(self) -> dict[str, object]:
        return {
            "metadata": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "graph_type": "manual_typing_pep_knowledge_graph",
                "schema_version": "1.0",
            },
            "nodes": [node.to_dict() for node in sorted(self.nodes.values(), key=lambda n: n.id)],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    def write_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.export(), indent=2, sort_keys=True), encoding="utf-8")

    def write_graphml(self, path: Path) -> None:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">', '<graph edgedefault="directed">']
        for node in self.nodes.values():
            lines.append(f'<node id="{html.escape(node.id)}"><data key="label">{html.escape(node.label)}</data><data key="type">{html.escape(node.type)}</data></node>')
        for i, edge in enumerate(self.edges):
            lines.append(f'<edge id="e{i}" source="{html.escape(edge.source)}" target="{html.escape(edge.target)}"><data key="type">{edge.type}</data><data key="confidence">{edge.confidence}</data></edge>')
        lines.extend(['</graph>', '</graphml>'])
        path.write_text("\n".join(lines), encoding="utf-8")
