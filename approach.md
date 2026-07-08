# Engineering Approach

## Problem Statement

The system models how Python typing evolved over time. It is designed as a knowledge-based reasoning system: source documents are converted into an explicit graph of entities, relationships, and evidence, and new inputs are answered by traversing and scoring that graph.

It is not a document search layer, chatbot, or wrapper around an extraction model. The central engineering goal is to make the knowledge representation and reasoning decisions visible in code and serialized output.

## Why Typing PEPs

Typing PEPs are a good domain for knowledge reasoning because the documents contain recurring design pressures: gradual typing, runtime compatibility, generic expressiveness, annotation syntax, static checker needs, and rejected alternatives. These PEPs are also connected historically. Later proposals often refine earlier decisions, reuse concepts, or deliberately avoid rejected designs.

The dataset is limited to closely related typing PEPs so the graph can represent why the language evolved rather than merely indexing a large document collection.

## Knowledge Representation

The graph uses explicit node types:

- `PEP`
- `Feature`
- `Concept`
- `Problem`
- `Decision`
- `Tradeoff`
- `RejectedAlternative`
- `Author`
- `PythonRelease`
- `Section`

These types separate document structure from design reasoning. For example, a `Section` node records where evidence came from, while a `Decision` node captures a design choice made by a PEP.

The graph uses typed relationships:

- `INTRODUCES`
- `SOLVES`
- `REFERENCES`
- `SUPERSEDES`
- `HAS_TRADEOFF`
- `REJECTS`
- `DISCUSSES`
- `AUTHORED_BY`
- `TARGETS_RELEASE`
- `RELATED_TO`

Every edge has confidence and evidence. Evidence includes source PEP, section, paragraph when available, sentence or excerpt, and the rule that created the edge. This is necessary because reasoning output should explain why a recommendation was selected.

## Extraction Design

Extraction is deterministic and rule-based:

1. The downloader retrieves the curated PEP files from the official Python PEP repository when network access allows it.
2. The parser extracts metadata, headings, sections, mentioned PEPs, and references.
3. The entity extractor applies curated keyword dictionaries, regex patterns, and section-aware rules.
4. The relationship extractor links nodes using explicit rules tied to metadata, sections, PEP mentions, rejected sections, and feature patterns.
5. The graph builder stores the resulting nodes and edges in a small custom adjacency-list graph.
6. The serializer writes parsed document summaries, JSON, and GraphML so the state can be inspected without running Python code.

Automatic entity extraction and relation extraction are intentionally avoided. The project should be understandable by reading the rules.

## Reasoning Algorithm

The reasoner accepts a new user input and follows this process:

1. Parse the input with keyword and PEP-reference rules.
2. Map detected concepts to graph concept nodes.
3. Score each PEP node using deterministic components.
4. Traverse graph relationships around the best PEPs.
5. Return structured JSON with recommendations and supporting evidence.

The score is intentionally simple:

```text
overall =
  40% concept overlap
  30% explicitly shared PEP reference
  20% graph distance from requested concepts
  10% supporting relationship count
```

The weights favor conceptual relevance, then direct PEP references, then graph proximity, then evidence density. This makes the score explainable and easy to adjust.

## Engineering Tradeoffs

- A custom graph keeps the dependency surface small and makes traversal behavior explicit.
- Rule-based extraction is less flexible than statistical extraction, but it is predictable and auditable.
- Tests use small in-memory parser fixtures; repository data is obtained through the official downloader rather than embedded placeholder PEPs.
- Section parsing is intentionally lightweight. It handles common PEP RST heading patterns without trying to become a full reStructuredText parser.
- Scoring favors readability over machine-learned ranking quality.

## Limitations

- The build requires official PEP files in `data/raw/`; if network access is blocked, downloading must be retried in an environment with repository access.
- Some PEPs use unique section names, so not every meaningful paragraph is extracted.
- Regex rules may miss concepts expressed with unusual wording.
- Confidence values are rule confidence estimates, not statistical probabilities.
- The reasoner currently scores PEPs, not arbitrary design paths.

## Future Improvements

- Add richer manually curated mappings for each selected PEP.
- Persist processed parsed documents under `data/processed/`.
- Add a small graph visualization image in addition to GraphML.
- Add more relationship rules for supersession, dependency, and compatibility.
- Add CLI options for showing complete reasoning chains and graph paths.
