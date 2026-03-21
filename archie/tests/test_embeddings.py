"""Tests for the embeddings module."""
import pytest
import tempfile
import shutil
from pathlib import Path
from archie.engine.embeddings import EmbeddingsStore


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for the database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def embeddings_store(temp_db_path):
    """Create an embeddings store."""
    return EmbeddingsStore(temp_db_path)


def test_embed_node(embeddings_store):
    """Test embedding a node."""
    node = {
        "id": "func:test.py:validate_card",
        "file_path": "test.py",
        "name": "validate_card",
        "type": "function",
        "params": ["card"]
    }
    
    embeddings_store.embed_node(node)
    stats = embeddings_store.get_stats()
    assert stats["total_embeddings"] == 1


def test_search(embeddings_store):
    """Test semantic search."""
    nodes = [
        {
            "id": "func:test.py:validate_card",
            "file_path": "test.py",
            "name": "validate_card",
            "type": "function",
            "params": ["card"]
        },
        {
            "id": "func:test.py:validate_email",
            "file_path": "test.py",
            "name": "validate_email",
            "type": "function",
            "params": ["email"]
        }
    ]
    
    for node in nodes:
        embeddings_store.embed_node(node)
    
    results = embeddings_store.search("card validation", top_k=1)
    assert len(results) > 0
    assert "validate_card" in results[0]["name"]



def test_find_duplicate(embeddings_store):
    """Test finding duplicate functions."""
    nodes = [
        {
            "id": "func:file1.py:validate_email",
            "file_path": "file1.py",
            "name": "validate_email",
            "type": "function",
            "params": ["email"]
        },
        {
            "id": "func:file2.py:validate_email",
            "file_path": "file2.py",
            "name": "validate_email",
            "type": "function",
            "params": ["email"]
        }
    ]
    
    for node in nodes:
        embeddings_store.embed_node(node)
    
    duplicates = embeddings_store.find_duplicate("email validation function")
    assert len(duplicates) >= 2


def test_remove_by_file(embeddings_store):
    """Test removing embeddings by file."""
    nodes = [
        {
            "id": "func:file1.py:func1",
            "file_path": "file1.py",
            "name": "func1",
            "type": "function"
        },
        {
            "id": "func:file2.py:func2",
            "file_path": "file2.py",
            "name": "func2",
            "type": "function"
        }
    ]
    
    for node in nodes:
        embeddings_store.embed_node(node)
    
    embeddings_store.remove_by_file("file1.py")
    results = embeddings_store.search("func1", top_k=10)
    
    # Should not find func1 anymore
    func1_results = [r for r in results if "func1" in r["name"]]
    assert len(func1_results) == 0
