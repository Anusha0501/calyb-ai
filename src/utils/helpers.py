"""Small shared helpers."""
from __future__ import annotations
import re

def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

def node_id(node_type: str, value: str | int) -> str:
    return f"{node_type.lower()}:{slugify(str(value))}"

def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`])", " ".join(text.split()))
    return [part.strip() for part in parts if part.strip()]

def first_sentence(text: str, limit: int = 260) -> str:
    sentences = split_sentences(text)
    sample = sentences[0] if sentences else " ".join(text.split())
    return sample[:limit]
