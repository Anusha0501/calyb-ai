"""Deterministic recommendation scoring."""
from __future__ import annotations
from dataclasses import dataclass
from src.graph.graph_storage import KnowledgeGraph
from src.reasoning.input_parser import ParsedInput

@dataclass(frozen=True)
class ScoreBreakdown:
    concept_overlap: float
    shared_pep_reference: float
    graph_distance: float
    support: float
    overall: float

class Scorer:
    """Score PEP recommendations with documented, deterministic components."""

    def score_pep(self, graph: KnowledgeGraph, parsed: ParsedInput, pep_id: str) -> ScoreBreakdown:
        pep_edges = [edge for edge in graph.edges if edge.source == pep_id or edge.target == pep_id]
        reachable = set(graph.related_nodes(pep_id, max_depth=2))
        adjacent = {edge.target if edge.source == pep_id else edge.source for edge in pep_edges}
        reachable.update(adjacent)

        concept_overlap = len(parsed.concept_ids & reachable) / max(len(parsed.concept_ids), 1)
        referenced = 1.0 if pep_id in parsed.pep_ids else 0.0

        distance_scores: list[float] = []
        for concept in parsed.concept_ids:
            path = graph.shortest_path(pep_id, concept)
            if path:
                distance_scores.append(max(0.0, 1.0 - ((len(path) - 1) / 4)))
        graph_distance = sum(distance_scores) / len(distance_scores) if distance_scores else 0.0
        support = min(len(pep_edges) / 10, 1.0)
        overall = (.40 * concept_overlap) + (.30 * referenced) + (.20 * graph_distance) + (.10 * support)
        return ScoreBreakdown(round(concept_overlap, 3), round(referenced, 3), round(graph_distance, 3), round(support, 3), round(overall, 3))
