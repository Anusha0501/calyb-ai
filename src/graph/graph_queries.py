"""Convenience graph query functions."""
from __future__ import annotations
from src.graph.graph_storage import KnowledgeGraph
from src.models.edge import Edge
from src.models.node import Node

class GraphQueries:
    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def nodes_by_type(self, node_type: str) -> list[Node]:
        return [node for node in self.graph.nodes.values() if node.type == node_type]

    def edges_for_node(self, node_id: str) -> list[Edge]:
        return [edge for edge in self.graph.edges if edge.source == node_id or edge.target == node_id]

    def peps_for_concepts(self, concept_ids: set[str]) -> set[str]:
        peps: set[str] = set()
        for edge in self.graph.edges:
            if edge.source in concept_ids or edge.target in concept_ids:
                for endpoint in (edge.source, edge.target):
                    if endpoint.startswith("pep:"):
                        peps.add(endpoint)
        return peps
