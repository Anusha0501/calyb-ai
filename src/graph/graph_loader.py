"""Load serialized knowledge state into the graph object."""
from __future__ import annotations
import json
from pathlib import Path
from src.graph.graph_storage import KnowledgeGraph
from src.models.edge import Edge, Evidence
from src.models.node import Node

def load_graph(path: Path) -> KnowledgeGraph:
    payload = json.loads(path.read_text(encoding="utf-8"))
    graph = KnowledgeGraph()
    for raw in payload["nodes"]:
        graph.add_node(Node(raw["id"], raw["type"], raw["label"], raw.get("metadata", {})))
    for raw in payload["edges"]:
        ev = raw["evidence"]
        graph.add_edge(Edge(raw["source"], raw["target"], raw["type"], raw["confidence"], Evidence(ev["source_pep"], ev["section"], ev["paragraph"], ev["sentence"], ev["rule"]), raw.get("metadata", {})))
    return graph
