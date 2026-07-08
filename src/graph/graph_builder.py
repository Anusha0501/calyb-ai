"""Build a knowledge graph from parsed PEP documents."""
from __future__ import annotations
from src.extractor.entity_extractor import EntityExtractor
from src.extractor.relationship_extractor import RelationshipExtractor
from src.graph.graph_storage import KnowledgeGraph
from src.models.pep import PepDocument

class GraphBuilder:
    def __init__(self) -> None:
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()

    def build(self, peps: list[PepDocument]) -> KnowledgeGraph:
        graph = KnowledgeGraph()
        for pep in peps:
            nodes = self.entity_extractor.extract(pep)
            for node in nodes:
                graph.add_node(node)
            for edge in self.relationship_extractor.extract(pep, nodes):
                graph.add_edge(edge)
        return graph
