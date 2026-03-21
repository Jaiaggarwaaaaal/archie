"""Example usage of Archie components."""
import json
from pathlib import Path
from archie.engine.parser import CodeParser
from archie.engine.graph import CodeGraph
from archie.engine.embeddings import EmbeddingsStore
from archie.engine.indexer import CodeIndexer
from archie.incident.listener import IncidentParser


def demo_parser():
    """Demo the parser."""
    print("=" * 60)
    print("DEMO: Parser")
    print("=" * 60)
    
    parser = CodeParser()
    sample_file = Path(__file__).parent / "tests" / "fixtures" / "sample_repo" / "payment.py"
    
    result = parser.parse_file(str(sample_file))
    print(f"\nParsed: {sample_file.name}")
    print(f"Functions found: {len(result['functions'])}")
    print(f"Classes found: {len(result['classes'])}")
    print(f"Imports found: {len(result['imports'])}")
    
    for func in result['functions']:
        print(f"  - {func['name']} (lines {func['line_start']}-{func['line_end']})")


def demo_graph():
    """Demo the graph."""
    print("\n" + "=" * 60)
    print("DEMO: Knowledge Graph")
    print("=" * 60)
    
    parser = CodeParser()
    graph = CodeGraph()
    
    sample_dir = Path(__file__).parent / "tests" / "fixtures" / "sample_repo"
    
    # Parse and add files
    for py_file in sample_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            parsed = parser.parse_file(str(py_file))
            if parsed:
                graph.add_file(parsed)
    
    stats = graph.get_stats()
    print(f"\nGraph Statistics:")
    print(f"  Files: {stats['files']}")
    print(f"  Functions: {stats['functions']}")
    print(f"  Classes: {stats['classes']}")
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Total edges: {stats['total_edges']}")
    
    # Demo: Find callers
    print("\nWho calls 'validate_card'?")
    callers = graph.get_callers("validate_card")
    for caller in callers:
        print(f"  - {caller['name']} in {caller.get('file_path', 'unknown')}")


def demo_incident_parser():
    """Demo incident parsing."""
    print("\n" + "=" * 60)
    print("DEMO: Incident Parser")
    print("=" * 60)
    
    parser = IncidentParser("test_secret")
    
    # Load Sentry payload
    sentry_file = Path(__file__).parent / "tests" / "fixtures" / "incident_payloads" / "sentry_payload.json"
    with open(sentry_file) as f:
        payload = json.load(f)
    
    incident = parser.parse(payload)
    
    print(f"\nParsed Incident:")
    print(f"  Source: {incident.source}")
    print(f"  Title: {incident.title}")
    print(f"  Error: {incident.error_message}")
    print(f"  Affected files: {', '.join(incident.affected_files)}")
    print(f"  Timestamp: {incident.timestamp}")


if __name__ == "__main__":
    print("\n🤖 Archie Component Demos\n")
    
    demo_parser()
    demo_graph()
    demo_incident_parser()
    
    print("\n" + "=" * 60)
    print("✅ All demos complete!")
    print("=" * 60)
