"""Command-line interface for the typing PEP knowledge system."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from src.config import GRAPHML_PATH, KNOWLEDGE_STATE_PATH, PROCESSED_DIR
from src.graph.graph_builder import GraphBuilder
from src.graph.graph_loader import load_graph
from src.loader import PepDownloader
from src.models.pep import PepDocument
from src.parser import PepParser
from src.reasoning.reasoner import Reasoner

def _write_processed_documents(peps: list[PepDocument]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    payload = []
    for pep in peps:
        payload.append({
            "number": pep.number,
            "title": pep.title,
            "authors": pep.authors,
            "status": pep.status,
            "python_version": pep.python_version,
            "type": pep.type,
            "created": pep.created,
            "mentioned_peps": sorted(pep.mentioned_peps),
            "references": pep.references,
            "sections": {
                slug: {"title": section.title, "paragraph_count": len(section.paragraphs), "preview": section.paragraphs[:2]}
                for slug, section in pep.sections.items()
            },
        })
    (PROCESSED_DIR / "parsed_peps.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

def download_dataset(force: bool = False) -> None:
    result = PepDownloader().download_all(force=force)
    if result.failed:
        print("Some PEPs failed to download. Re-run the command after fixing network access.")

def build_graph(force_download: bool = False) -> None:
    downloader = PepDownloader()
    if force_download or not downloader.existing_paths():
        result = downloader.download_all(force=force_download)
        if result.failed:
            print("Continuing with successfully downloaded files only.")
    paths = downloader.existing_paths()
    if not paths:
        raise SystemExit("No PEP files found in data/raw. Run `python -m src.main download` with network access first.")
    parser = PepParser()
    peps = [parser.parse_file(path) for path in paths]
    _write_processed_documents(peps)
    graph = GraphBuilder().build(peps)
    graph.write_json(KNOWLEDGE_STATE_PATH)
    graph.write_graphml(GRAPHML_PATH)
    print(f"Wrote {KNOWLEDGE_STATE_PATH}, {GRAPHML_PATH}, and {PROCESSED_DIR / 'parsed_peps.json'}")

def reason(query: str, knowledge_path: Path = KNOWLEDGE_STATE_PATH) -> None:
    graph = load_graph(knowledge_path)
    print(json.dumps(Reasoner(graph).reason(query), indent=2))

def stats(knowledge_path: Path = KNOWLEDGE_STATE_PATH) -> None:
    graph = load_graph(knowledge_path)
    node_types = {}
    for node in graph.nodes.values():
        node_type = node.type
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    total_nodes = len(graph.nodes)
    total_relationships = len(graph.edges)
    
    print("Knowledge Graph Statistics")
    print()
    for node_type, count in sorted(node_types.items()):
        print(f"{node_type}: {count}")
    print()
    print(f"Total Nodes: {total_nodes}")
    print(f"Total Relationships: {total_relationships}")

def main() -> None:
    ap = argparse.ArgumentParser(description="Build and query a typing PEP knowledge graph.")
    sub = ap.add_subparsers(dest="command", required=True)
    d = sub.add_parser("download", help="Download selected official PEP RST files into data/raw.")
    d.add_argument("--force", action="store_true", help="Re-download files even when they already exist.")
    b = sub.add_parser("build", help="Parse PEPs, extract knowledge, and serialize the graph.")
    b.add_argument("--force-download", action="store_true", help="Re-download the dataset before building.")
    q = sub.add_parser("reason", help="Run deterministic reasoning for a new input.")
    q.add_argument("query")
    s = sub.add_parser("stats", help="Print knowledge graph statistics.")
    args = ap.parse_args()
    if args.command == "download":
        download_dataset(args.force)
    elif args.command == "build":
        build_graph(args.force_download)
    elif args.command == "reason":
        reason(args.query)
    elif args.command == "stats":
        stats()

if __name__ == "__main__":
    main()
