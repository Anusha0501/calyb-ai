"""Knowledge graph edge model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Evidence:
    """Explainable provenance for an extracted relationship."""
    source_pep: int
    section: str
    paragraph: int | None
    sentence: str
    rule: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_pep": self.source_pep,
            "section": self.section,
            "paragraph": self.paragraph,
            "sentence": self.sentence,
            "rule": self.rule,
        }

@dataclass(frozen=True)
class Edge:
    """A typed, evidenced relationship between two nodes."""
    source: str
    target: str
    type: str
    confidence: float
    evidence: Evidence
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "confidence": self.confidence,
            "evidence": self.evidence.to_dict(),
            "metadata": self.metadata,
        }
