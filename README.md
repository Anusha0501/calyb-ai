# Python Typing PEP Knowledge Reasoning System

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](https://github.com)

A deterministic knowledge-based reasoning system for understanding how Python typing evolved across a curated set of Python Enhancement Proposals.

The project loads typing-related PEPs, parses their structure, extracts manually defined entities and relationships, builds an explainable knowledge graph, and answers new user questions with structured recommendations backed by graph evidence.

## Project Status

✅ **Core Features Complete**
- PEP downloader with official repository integration
- RST parser for PEP structure extraction
- Rule-based entity and relationship extraction
- Knowledge graph construction with multiple node types
- Deterministic reasoning engine with evidence tracking
- JSON and GraphML export capabilities
- Comprehensive test suite (6/6 tests passing)
- CLI with download, build, reason, and stats commands

## Features

### Knowledge Graph
- **516 nodes** across 11 types: PEP, Feature, Concept, Decision, Tradeoff, RejectedAlternative, Problem, Author, PythonRelease, Section, External
- **1,615 relationships** with typed edges and confidence scores
- Explainable evidence trails for every relationship
- GraphML export for visualization in Gephi, Cytoscape, or other tools

### Reasoning Engine
- Concept-based query parsing
- Deterministic scoring with transparent weights
- Evidence-backed recommendations
- Suggested reading order based on graph topology
- Confidence scores for all results

## Architecture

```text
PEP downloader -> PEP parser -> entity extractor -> relationship extractor
      -> graph builder -> knowledge_state.json / graph.graphml -> reasoner
```

The implementation is intentionally rule-based. Entity types, relationship types, extraction rules, and scoring logic are defined in code instead of delegated to automatic graph construction or language-model extraction.

## Dataset

The curated dataset focuses on Python typing evolution PEPs, including PEP 484, 526, 544, 563, 585, 589, 604, 612, 646, 647, 673, 695, and related typing proposals.

The downloader targets the official Python PEP repository and stores complete `.rst` files in `data/raw/`. The repository does not embed shortened PEP samples; clone users should run the download command to reproduce the dataset.

## Requirements

- Python 3.11 or higher
- Network access for initial PEP download
- Virtual environment (recommended)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd calyb-ai

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
pip install -e .

# Install development dependencies
pip install pytest>=8.0
```

## Quick Start

### 1. Download PEP Dataset

```bash
python -m src.main download
```

This downloads 26 typing-related PEPs from the official Python repository to `data/raw/`. Use `--force` to re-download existing files.

### 2. Build Knowledge Graph

```bash
python -m src.main build
```

This parses the PEPs, extracts entities and relationships, and generates:
- `knowledge_state.json` - Complete graph with metadata
- `graph.graphml` - GraphML format for visualization
- `data/processed/parsed_peps.json` - Parsed PEP metadata

### 3. Query the Knowledge Graph

```bash
python -m src.main reason "I want runtime type checking"
python -m src.main reason "Why was Protocol introduced?"
python -m src.main reason "How should generic types evolve?"
```

### 4. View Statistics

```bash
python -m src.main stats
```

Output includes node type distribution and total relationship count.

## CLI Commands

| Command | Description | Options |
|---------|-------------|---------|
| `download` | Download PEP files from official repository | `--force` to re-download |
| `build` | Parse PEPs and build knowledge graph | `--force-download` to re-download first |
| `reason <query>` | Query the knowledge graph | Query string required |
| `stats` | Display graph statistics | None |

## Example Output

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

The actual output includes detailed evidence with confidence scores, source PEP references, and relationship types.

## Project Structure

```
calyb-ai/
├── data/
│   ├── raw/              # Downloaded PEP .rst files
│   └── processed/        # Parsed PEP metadata
├── src/
│   ├── extractor/        # Entity and relationship extraction
│   ├── graph/           # Graph building and storage
│   ├── models/          # Node and edge data models
│   ├── reasoning/       # Query parsing and reasoning
│   ├── utils/           # Helper functions
│   ├── config.py        # Configuration constants
│   ├── loader.py        # PEP downloader
│   ├── main.py          # CLI entry point
│   └── parser.py        # RST parser
├── tests/               # Test suite
├── knowledge_state.json # Serialized knowledge graph
├── graph.graphml        # GraphML export
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── approach.md         # Engineering approach documentation
```

## Testing

Run the test suite:

```bash
pytest
```

All tests use in-memory fixtures and do not require downloaded PEP files.

## Graph Visualization

Import `graph.graphml` into:
- **Gephi** (https://gephi.org) - Open-source graph visualization platform
- **Cytoscape** (https://cytoscape.org) - Network analysis and visualization
- **yEd** (https://www.yworks.com/products/yed) - Graph editing and layout

The graph includes typed nodes and edges with confidence scores, enabling rich visual analysis of PEP relationships.

## Contributing

Contributions are welcome! Areas for improvement:
- Additional PEP coverage
- Enhanced extraction rules
- New relationship types
- Improved scoring algorithms
- Additional CLI features

## License

MIT License - See LICENSE file for details.

## Citation

If you use this project in your research, please cite:

```
Python Typing PEP Knowledge Reasoning System
https://github.com/yourusername/calyb-ai
```
