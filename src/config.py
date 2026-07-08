"""Project configuration."""
from __future__ import annotations
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
KNOWLEDGE_STATE_PATH = ROOT_DIR / "knowledge_state.json"
GRAPHML_PATH = ROOT_DIR / "graph.graphml"

PEP_NUMBERS: tuple[int, ...] = (
    3107, 483, 484, 526, 544, 560, 563, 585, 586, 589,
    591, 593, 604, 612, 613, 646, 647, 655, 673, 675,
    681, 692, 695, 696, 698, 705,
)

PEP_RAW_URL = "https://raw.githubusercontent.com/python/peps/main/peps/pep-{pep:04d}.rst"
IMPORTANT_SECTIONS = {
    "abstract", "motivation", "rationale", "specification", "rejected ideas",
    "rejected alternatives", "rejected/postponed ideas", "backwards compatibility",
    "reference implementation", "references", "introduction", "type aliases",
}
