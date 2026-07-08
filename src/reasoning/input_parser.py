"""Parse new user requests into deterministic concept signals."""
from __future__ import annotations
import re
from dataclasses import dataclass
from src.extractor.entity_extractor import CONCEPT_KEYWORDS
from src.utils.helpers import node_id

@dataclass(frozen=True)
class ParsedInput:
    text: str
    concept_ids: set[str]
    pep_ids: set[str]
    tokens: set[str]

class InputParser:
    def parse(self, text: str) -> ParsedInput:
        lower = text.lower()
        concepts = {node_id("concept", concept) for concept, keywords in CONCEPT_KEYWORDS.items() if any(keyword in lower for keyword in keywords)}
        peps = {f"pep:{int(match)}" for match in re.findall(r"\bPEP\s*([0-9]{3,4})\b", text, flags=re.IGNORECASE)}
        tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", lower))
        return ParsedInput(text=text, concept_ids=concepts, pep_ids=peps, tokens=tokens)
