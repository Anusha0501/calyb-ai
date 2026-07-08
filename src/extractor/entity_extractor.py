"""Manual, rule-based entity extraction for typing PEPs."""
from __future__ import annotations
import re
from src.models.node import Node
from src.models.pep import PepDocument
from src.utils.helpers import first_sentence, node_id, slugify

CONCEPT_KEYWORDS: dict[str, list[str]] = {
    "type hints": ["type hint", "type hints", "annotation", "annotations"],
    "generic types": ["generic", "generics", "parameterized", "type parameter"],
    "gradual typing": ["gradual typing", "static typing", "type checker"],
    "protocols": ["protocol", "structural subtyping"],
    "typed dictionaries": ["typeddict", "typed dictionary"],
    "union syntax": ["union", "optional", "|"],
    "variadic generics": ["variadic", "typevartuple", "unpack"],
    "callable parameter specification": ["paramspec", "callable", "decorator"],
    "self type": ["self type", "typing.self"],
    "type aliases": ["type alias", "typealias", "type statement"],
    "literal types": ["literal"],
    "type narrowing": ["typeguard", "typeis", "narrowing"],
    "override safety": ["override", "overriding"],
    "read-only items": ["readonly", "read-only"],
}

FEATURE_PATTERNS: dict[str, str] = {
    r"\bTypeVarTuple\b": "TypeVarTuple",
    r"\bParamSpec\b": "ParamSpec",
    r"\bTypedDict\b": "TypedDict",
    r"\bProtocol\b": "Protocol",
    r"\bTypeGuard\b": "TypeGuard",
    r"\bSelf\b": "Self",
    r"\bLiteral\b": "Literal",
    r"\bRequired\b|\bNotRequired\b": "Required and NotRequired",
    r"\bReadOnly\b": "ReadOnly",
    r"\boverride\b|\bOverride\b": "override decorator",
    r"\btype\s+statement\b|\bTypeAlias\b": "type aliases",
    r"\bCallable\b": "Callable typing",
    r"\bUnion\b|\|": "union types",
    r"\blist\[|dict\[|tuple\[": "built-in generic aliases",
}

class EntityExtractor:
    """Extract nodes using curated typing-domain rules."""

    def extract(self, pep: PepDocument) -> list[Node]:
        nodes: dict[str, Node] = {}
        self._add(nodes, Node(f"pep:{pep.number}", "PEP", f"PEP {pep.number}: {pep.title}", {
            "number": pep.number, "title": pep.title, "status": pep.status,
            "python_version": pep.python_version, "created": pep.created, "pep_type": pep.type,
        }))
        for author in pep.authors:
            self._add(nodes, Node(node_id("author", author), "Author", author, {}))
        if pep.python_version:
            self._add(nodes, Node(node_id("python_release", pep.python_version), "PythonRelease", pep.python_version, {}))
        for section in pep.sections.values():
            sid = f"section:pep_{pep.number}:{section.slug}"
            self._add(nodes, Node(sid, "Section", f"PEP {pep.number} {section.title}", {
                "pep": pep.number, "title": section.title, "slug": section.slug,
                "summary": first_sentence(section.text),
            }))
            self._extract_section_entities(nodes, pep, section.slug, section.paragraphs)
        return list(nodes.values())

    def _extract_section_entities(self, nodes: dict[str, Node], pep: PepDocument, slug: str, paragraphs: list[str]) -> None:
        text = "\n".join(paragraphs)
        lower = text.lower()
        for concept, keywords in CONCEPT_KEYWORDS.items():
            if any(keyword in lower for keyword in keywords):
                self._add(nodes, Node(node_id("concept", concept), "Concept", concept, {"keywords": keywords}))
        for pattern, feature in FEATURE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                self._add(nodes, Node(node_id("feature", feature), "Feature", feature, {"source_pep": pep.number}))
        if slug in {"motivation", "rationale", "abstract"}:
            for index, paragraph in enumerate(paragraphs[:4]):
                if self._looks_like_problem(paragraph):
                    label = first_sentence(paragraph, 120)
                    self._add(nodes, Node(f"problem:pep_{pep.number}:{slug}:{index}", "Problem", label, {"source_pep": pep.number, "section": slug, "paragraph": index}))
        if slug in {"rationale", "specification", "abstract"}:
            for index, paragraph in enumerate(paragraphs[:4]):
                if self._looks_like_decision(paragraph):
                    label = first_sentence(paragraph, 120)
                    self._add(nodes, Node(f"decision:pep_{pep.number}:{slug}:{index}", "Decision", label, {"source_pep": pep.number, "section": slug, "paragraph": index}))
        if "rejected" in slug:
            for index, paragraph in enumerate(paragraphs[:8]):
                label = first_sentence(paragraph, 120)
                self._add(nodes, Node(f"rejected:pep_{pep.number}:{index}", "RejectedAlternative", label, {"source_pep": pep.number, "section": slug, "paragraph": index}))
        if any(word in lower for word in ("trade-off", "tradeoff", "drawback", "cost", "backwards compatibility", "limitation")):
            tradeoff_paragraph = next((i for i, paragraph in enumerate(paragraphs) if any(word in paragraph.lower() for word in ("trade-off", "tradeoff", "drawback", "cost", "backwards compatibility", "limitation"))), None)
            self._add(nodes, Node(f"tradeoff:pep_{pep.number}:{slug}", "Tradeoff", f"Tradeoffs in PEP {pep.number} {slug.replace('_', ' ')}", {"source_pep": pep.number, "section": slug, "paragraph": tradeoff_paragraph}))

    def _looks_like_problem(self, paragraph: str) -> bool:
        return any(word in paragraph.lower() for word in ("problem", "difficult", "cannot", "need", "motivation", "currently", "lack"))

    def _looks_like_decision(self, paragraph: str) -> bool:
        return any(word in paragraph.lower() for word in ("this pep", "proposal", "introduces", "specifies", "allows", "provides"))

    def _add(self, nodes: dict[str, Node], node: Node) -> None:
        nodes.setdefault(node.id, node)
