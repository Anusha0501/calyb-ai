"""Manual relationship extraction rules for parsed typing PEPs."""
from __future__ import annotations
import re
from src.extractor.entity_extractor import CONCEPT_KEYWORDS, FEATURE_PATTERNS
from src.models.edge import Edge, Evidence
from src.models.node import Node
from src.models.pep import PepDocument, Section
from src.utils.helpers import first_sentence, node_id, split_sentences

class RelationshipExtractor:
    """Create evidenced edges with deterministic section-aware rules."""

    def extract(self, pep: PepDocument, nodes: list[Node]) -> list[Edge]:
        node_map = {node.id: node for node in nodes}
        edges: list[Edge] = []
        pep_id = f"pep:{pep.number}"
        for author in pep.authors:
            edges.append(self._edge(pep_id, node_id("author", author), "AUTHORED_BY", .99, pep, "Header", None, f"Author: {author}", "metadata_author"))
        if pep.python_version:
            edges.append(self._edge(pep_id, node_id("python_release", pep.python_version), "TARGETS_RELEASE", .95, pep, "Header", None, f"Python-Version: {pep.python_version}", "metadata_python_version"))
        for mentioned in sorted(pep.mentioned_peps):
            rel_type = "DEPENDS_ON" if self._dependency_context(pep.raw_text, mentioned) else "REFERENCES"
            edges.append(self._edge(pep_id, f"pep:{mentioned}", rel_type, .78, pep, "Full Text", None, f"PEP {mentioned} is mentioned by PEP {pep.number}.", "mentioned_pep_regex"))
        for section in pep.sections.values():
            sid = f"section:pep_{pep.number}:{section.slug}"
            edges.append(self._edge(pep_id, sid, "DISCUSSES", .90, pep, section.title, None, first_sentence(section.text), "pep_discusses_section"))
            self._section_relationships(edges, pep, section, node_map)
        return edges

    def _section_relationships(self, edges: list[Edge], pep: PepDocument, section: Section, node_map: dict[str, Node]) -> None:
        section_id = f"section:pep_{pep.number}:{section.slug}"
        text = section.text
        lower = text.lower()
        for concept, keywords in CONCEPT_KEYWORDS.items():
            cid = node_id("concept", concept)
            if cid in node_map and any(keyword in lower for keyword in keywords):
                paragraph, sentence = self._evidence_sentence(section, keywords)
                edges.append(self._edge(section_id, cid, "RELATED_TO", .74, pep, section.title, paragraph, sentence, "section_keyword_concept"))
        for pattern, feature in FEATURE_PATTERNS.items():
            fid = node_id("feature", feature)
            if fid in node_map and re.search(pattern, text, re.IGNORECASE):
                paragraph, sentence = self._evidence_sentence(section, [feature])
                edges.append(self._edge(f"pep:{pep.number}", fid, "INTRODUCES", .82, pep, section.title, paragraph, sentence, "feature_detection_v1"))
                edges.append(self._edge(section_id, fid, "DISCUSSES", .78, pep, section.title, paragraph, sentence, "section_feature_pattern"))
        for node in node_map.values():
            if node.metadata.get("source_pep") != pep.number or node.metadata.get("section") != section.slug:
                continue
            paragraph = node.metadata.get("paragraph")
            if node.type == "Problem":
                edges.append(self._edge(f"pep:{pep.number}", node.id, "SOLVES", .70, pep, section.title, paragraph, node.label, "motivation_problem_rule"))
                edges.append(self._edge(section_id, node.id, "MOTIVATION", .82, pep, section.title, paragraph, node.label, "motivation_section_rule"))
            elif node.type == "Decision":
                edges.append(self._edge(f"pep:{pep.number}", node.id, "DISCUSSES", .78, pep, section.title, paragraph, node.label, "decision_from_rationale"))
            elif node.type == "RejectedAlternative":
                edges.append(self._edge(f"pep:{pep.number}", node.id, "REJECTS", .86, pep, section.title, paragraph, node.label, "rejected_because_rule"))
            elif node.type == "Tradeoff":
                p, sentence = self._evidence_sentence(section, ["trade", "compatibility", "cost", "drawback"])
                edges.append(self._edge(f"pep:{pep.number}", node.id, "HAS_TRADEOFF", .78, pep, section.title, p, sentence, "tradeoff_keyword"))
                if "compatibility" in lower:
                    edges.append(self._edge(f"pep:{pep.number}", node.id, "BACKWARDS_COMPATIBILITY", .80, pep, section.title, p, sentence, "backwards_compatibility_section"))
        for sentence in split_sentences(text):
            for superseded in re.findall(r"supersed(?:e|ed|es)\s+PEP\s+([0-9]{3,4})", sentence, flags=re.IGNORECASE):
                edges.append(self._edge(f"pep:{pep.number}", f"pep:{int(superseded)}", "SUPERSEDES", .90, pep, section.title, None, sentence, "supersedes_sentence"))
            for replaced in re.findall(r"replac(?:e|ed|es)\s+PEP\s+([0-9]{3,4})", sentence, flags=re.IGNORECASE):
                edges.append(self._edge(f"pep:{pep.number}", f"pep:{int(replaced)}", "REPLACES", .86, pep, section.title, None, sentence, "replaces_sentence"))

    def _dependency_context(self, text: str, mentioned: int) -> bool:
        pattern = re.compile(rf"(?:depends on|requires|builds on|extends).{{0,80}}(?:PEP\s+{mentioned}|:pep:`{mentioned}`)", re.IGNORECASE | re.DOTALL)
        return bool(pattern.search(text))

    def _evidence_sentence(self, section: Section, keywords: list[str]) -> tuple[int | None, str]:
        for paragraph_index, paragraph in enumerate(section.paragraphs):
            for sentence in split_sentences(paragraph):
                if any(keyword.lower() in sentence.lower() for keyword in keywords if keyword != "|"):
                    return paragraph_index, sentence[:300]
        return (0 if section.paragraphs else None), first_sentence(section.text)

    def _edge(self, source: str, target: str, rel_type: str, confidence: float, pep: PepDocument, section: str, paragraph: int | None, sentence: str, rule: str) -> Edge:
        return Edge(source, target, rel_type, confidence, Evidence(pep.number, section, paragraph, sentence, rule))
