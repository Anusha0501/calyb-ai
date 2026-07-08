"""Structured PEP document models."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Section:
    title: str
    slug: str
    text: str
    paragraphs: list[str]

@dataclass(frozen=True)
class PepDocument:
    number: int
    title: str
    authors: list[str]
    status: str
    python_version: str | None
    type: str | None
    created: str | None
    raw_text: str
    sections: dict[str, Section] = field(default_factory=dict)
    mentioned_peps: set[int] = field(default_factory=set)
    references: list[str] = field(default_factory=list)
