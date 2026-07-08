# Python Typing PEP Knowledge Reasoning System

A deterministic knowledge-based reasoning system for understanding how Python typing evolved across a curated set of Python Enhancement Proposals.

The project loads typing-related PEPs, parses their structure, extracts manually defined entities and relationships, builds an explainable knowledge graph, and answers new user questions with structured recommendations backed by graph evidence.

## Architecture

```text
PEP downloader -> PEP parser -> entity extractor -> relationship extractor
      -> graph builder -> knowledge_state.json / graph.graphml -> reasoner
```

The implementation is intentionally rule-based. Entity types, relationship types, extraction rules, and scoring logic are defined in code instead of delegated to automatic graph construction or language-model extraction.

## Dataset

The curated dataset focuses on Python typing evolution PEPs, including PEP 484, 526, 544, 563, 585, 589, 604, 612, 646, 647, 673, 695, and related typing proposals.

The downloader targets the official Python PEP repository and stores complete `.rst` files in `data/raw/`. The repository does not embed shortened PEP samples; clone users should run the download command to reproduce the dataset.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# or install package metadata directly
pip install -e .
```

## Download the Dataset

```bash
python -m src.main download
# force a fresh copy
python -m src.main download --force
```

The downloader creates `data/raw/`, skips files already present, retries failures, and reports failed PEP numbers without fabricating content.

## Build the Knowledge Graph

```bash
python -m src.main build
```

Outputs:

- `knowledge_state.json`: inspectable graph with metadata, nodes, edges, and evidence
- `graph.graphml`: graph visualization/export format
- `data/raw/`: downloaded official PEP source files
- `data/processed/parsed_peps.json`: parsed metadata and section previews

## Run Reasoning

```bash
python -m src.main reason "How did Python typing evolve?"
```

The reasoner returns structured JSON with relevant PEPs, decisions, rejected alternatives, tradeoffs, evidence, suggested reading order, and a confidence score.

## Example Output Shape

```json
{
  "ParsedConcepts": ["concept:callable_parameter_specification"],
  "RelevantPEPs": [],
  "HistoricalDecisions": [],
  "RejectedAlternatives": [],
  "Tradeoffs": [],
  "Evidence": [],
  "SuggestedReadingOrder": [],
  "ConfidenceScore": 0.0
}
```

## Folder Structure

```text
README.md
approach.md
requirements.txt
knowledge_state.json
graph.graphml
data/raw/
data/processed/
pyproject.toml
src/main.py
src/config.py
src/loader.py
src/parser.py
src/extractor/entity_extractor.py
src/extractor/relationship_extractor.py
src/graph/graph_builder.py
src/graph/graph_storage.py
src/graph/graph_queries.py
src/reasoning/input_parser.py
src/reasoning/reasoner.py
src/reasoning/scorer.py
src/models/node.py
src/models/edge.py
src/utils/helpers.py
tests/test_parser.py
tests/test_graph.py
tests/test_reasoner.py
```
