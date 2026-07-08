"""Rule-based parser for raw PEP reStructuredText files."""
from __future__ import annotations
import re
from pathlib import Path
from src.config import IMPORTANT_SECTIONS
from src.models.pep import PepDocument, Section
from src.utils.helpers import slugify

_HEADER_RE = re.compile(r"^(PEP|Title|Author|Status|Type|Created|Python-Version):\s*(.*)$")
_PEP_MENTION_RE = re.compile(r"(?:\bPEP\s+|:pep:`)([0-9]{3,4})`?", re.IGNORECASE)

class PepParser:
    """Parse metadata and semantically important sections from PEP RST text."""

    def parse_file(self, path: Path) -> PepDocument:
        return self.parse_text(path.read_text(encoding="utf-8"))

    def parse_text(self, text: str) -> PepDocument:
        metadata = self._parse_metadata(text)
        sections = self._parse_sections(text)
        references = self._extract_references(sections)
        mentioned = {int(match) for match in _PEP_MENTION_RE.findall(text)}
        number = int(metadata.get("PEP", "0"))
        mentioned.discard(number)
        return PepDocument(
            number=number,
            title=metadata.get("Title", "Untitled"),
            authors=self._parse_authors(metadata.get("Author", "")),
            status=metadata.get("Status", "Unknown"),
            python_version=metadata.get("Python-Version"),
            type=metadata.get("Type"),
            created=metadata.get("Created"),
            raw_text=text,
            sections=sections,
            mentioned_peps=mentioned,
            references=references,
        )

    def _parse_metadata(self, text: str) -> dict[str, str]:
        metadata: dict[str, str] = {}
        current: str | None = None
        for line in text.splitlines():
            if not line.strip() and metadata:
                break
            match = _HEADER_RE.match(line)
            if match:
                current = match.group(1)
                metadata[current] = match.group(2).strip()
            elif current and line.startswith(" "):
                metadata[current] += " " + line.strip()
        return metadata

    def _parse_sections(self, text: str) -> dict[str, Section]:
        lines = text.splitlines()
        headings: list[tuple[int, str]] = []
        for index in range(len(lines) - 1):
            title = lines[index].strip()
            underline = lines[index + 1].strip()
            if title and len(underline) >= len(title) and set(underline) <= set("=-`:'~^_#*+"):
                slug = slugify(title)
                if slug in IMPORTANT_SECTIONS or any(word in slug for word in ("rejected", "motivation", "rationale", "reference")):
                    headings.append((index, title))
        sections: dict[str, Section] = {}
        for pos, (start, title) in enumerate(headings):
            end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
            body = "\n".join(lines[start + 2:end]).strip()
            paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n", body) if p.strip()]
            sections[slugify(title)] = Section(title=title, slug=slugify(title), text=body, paragraphs=paragraphs)
        return sections

    def _parse_authors(self, raw: str) -> list[str]:
        cleaned = re.sub(r"<[^>]+>", "", raw)
        parts = re.split(r",\s*|\s+and\s+", cleaned)
        return [part.strip() for part in parts if part.strip()]

    def _extract_references(self, sections: dict[str, Section]) -> list[str]:
        refs: list[str] = []
        for slug, section in sections.items():
            if "reference" not in slug:
                continue
            refs.extend(p for p in section.paragraphs if p.startswith(".. [") or "http" in p)
        return refs
