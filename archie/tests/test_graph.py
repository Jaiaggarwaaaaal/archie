"""Tests for the graph module."""
import pytest
from pathlib import Path
from archie.engine.parser import CodeParser
from archie.engine.graph import CodeGraph


@pytest.fixture
def graph():
    return CodeGraph()


@pytest.fixture
def parser():
    return CodeParser()


@pytest.fixture
def sample_repo_path():
    return Path(__file__).parent / "fixtures" / "sample_repo"


@pytest.fixture
def parsed_validators(parser, sample_repo_path):
    return parser.parse_file(str(sample_repo_path / "validators.py"))


@pytest.fixture
def parsed_payment(parser, sample_repo_path):
    return parser.parse_file(str(sample_repo_path / "payment.py"))


def test_add_file(graph, parsed_validators):
    """Test adding a file to the graph."""
    graph.add_file(parsed_validators)
    
    stats = graph.get_stats()
    assert stats["files"] == 1
    assert stats["functions"] >= 3


def test_get_node(graph, parsed_validators):
    """Test retrieving a node by name."""
    graph.add_file(parsed_validators)
    
    node = graph.get_node("validate_card")
    assert node is not None
    assert node["type"] == "function"
    assert node["name"] == "validate_card"


def test_get_callers(graph, parsed_payment):
    """Test getting callers of a function."""
    graph.add_file(parsed_payment)
    
    callers = graph.get_callers("_charge")
    assert len(callers) > 0


def test_get_callees(graph, parsed_payment):
    """Test getting callees of a function."""
    graph.add_file(parsed_payment)
    
    callees = graph.get_callees("process_payment")
    callee_names = [c["name"] for c in callees]
    assert "validate_amount" in callee_names
    assert "validate_card" in callee_names


def test_subgraph_around(graph, parsed_validators):
    """Test getting subgraph around a node."""
    graph.add_file(parsed_validators)
    
    node = graph.get_node("validate_card")
    subgraph = graph.subgraph_around(node["id"], depth=1)
    
    assert len(subgraph["nodes"]) > 0
    assert "nodes" in subgraph
    assert "edges" in subgraph


def test_find_similar_nodes(graph, parsed_validators):
    """Test finding similar nodes."""
    graph.add_file(parsed_validators)
    
    similar = graph.find_similar_nodes("validate")
    assert len(similar) >= 3


def test_remove_file_nodes(graph, parsed_validators, parsed_payment):
    """Test removing file nodes."""
    graph.add_file(parsed_validators)
    graph.add_file(parsed_payment)
    
    initial_count = graph.get_stats()["total_nodes"]
    graph.remove_file_nodes(parsed_validators["file_path"])
    
    final_count = graph.get_stats()["total_nodes"]
    assert final_count < initial_count


def test_get_dependencies(graph, parsed_payment):
    """Test getting file dependencies."""
    graph.add_file(parsed_payment)
    
    deps = graph.get_dependencies(parsed_payment["file_path"])
    assert len(deps) > 0
