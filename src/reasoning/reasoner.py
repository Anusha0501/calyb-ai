"""Explainable graph reasoning over the typing PEP knowledge graph."""
from __future__ import annotations
from src.graph.graph_queries import GraphQueries
from src.graph.graph_storage import KnowledgeGraph
from src.reasoning.input_parser import InputParser
from src.reasoning.scorer import Scorer

class Reasoner:
    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph
        self.parser = InputParser()
        self.scorer = Scorer()
        self.queries = GraphQueries(graph)

    def reason(self, user_input: str, limit: int = 5) -> dict[str, object]:
        parsed = self.parser.parse(user_input)
        pep_ids = [node.id for node in self.queries.nodes_by_type("PEP")]
        scored = [(pep_id, self.scorer.score_pep(self.graph, parsed, pep_id)) for pep_id in pep_ids]
        scored.sort(key=lambda item: item[1].overall, reverse=True)
        selected = [(pep_id, score) for pep_id, score in scored if score.overall > 0][:limit]
        if not selected:
            selected = scored[:limit]
        evidence = []
        decisions = []
        rejected = []
        tradeoffs = []
        for pep_id, _score in selected:
            for edge in self.queries.edges_for_node(pep_id):
                node = self.graph.nodes.get(edge.target if edge.source == pep_id else edge.source)
                if not node:
                    continue
                ev = {"relationship": edge.type, "node": node.label, "source_pep": edge.evidence.source_pep, "section": edge.evidence.section, "sentence": edge.evidence.sentence, "confidence": edge.confidence}
                evidence.append(ev)
                if node.type == "Decision":
                    decisions.append(ev)
                elif node.type == "RejectedAlternative":
                    rejected.append(ev)
                elif node.type == "Tradeoff":
                    tradeoffs.append(ev)
        relevant = [{"pep": self.graph.nodes[pep_id].label, "id": pep_id, "score": score.overall, "score_breakdown": score.__dict__} for pep_id, score in selected]
        return {
            "ParsedConcepts": sorted(parsed.concept_ids),
            "RelevantPEPs": relevant,
            "HistoricalDecisions": decisions[:10],
            "RejectedAlternatives": rejected[:10],
            "Tradeoffs": tradeoffs[:10],
            "Evidence": evidence[:20],
            "SuggestedReadingOrder": [item["pep"] for item in relevant],
            "ConfidenceScore": round(sum(score.overall for _, score in selected) / max(len(selected), 1), 3),
        }
