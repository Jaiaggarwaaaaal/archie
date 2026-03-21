"""Tests for the indexer module."""
import pytest
import tempfile
import shutil
from pathlib import Path
from archie.engine.indexer import CodeIndexer


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for the database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def indexer(temp_db_path):
    """Create an indexer."""
    return CodeIndexer(temp_db_path)


@pytest.fixture
def sample_repo_path():
    return Path(__file__).parent / "fixtures" / "sample_repo"


def test_index_repo(indexer, sample_repo_path):
    """Test full repository indexing."""
    indexer.index_repo(str(sample_repo_path))
    
    summary = indexer.get_architecture_summary()
    assert summary["graph"]["files"] > 0
    assert summary["graph"]["functions"] > 0
    assert summary["embeddings"]["total_embeddings"] > 0


def test_update_file(indexer, sample_repo_path):
    """Test updating a single file."""
    file_path = str(sample_repo_path / "validators.py")
    indexer.update_file(file_path)
    
    # Check that functions were indexed
    node = indexer.graph.get_node("validate_card")
    assert node is not None


def test_incremental_update_no_duplicates(indexer, sample_repo_path):
    """Test that incremental updates don't create duplicates."""
    file_path = str(sample_repo_path / "validators.py")
    
    # Index twice
    indexer.update_file(file_path)
    initial_count = indexer.graph.get_stats()["total_nodes"]
    
    indexer.update_file(file_path)
    final_count = indexer.graph.get_stats()["total_nodes"]
    
    # Should be the same - no duplicates
    assert initial_count == final_count


def test_get_architecture_summary(indexer, sample_repo_path):
    """Test getting architecture summary."""
    indexer.index_repo(str(sample_repo_path))
    
    summary = indexer.get_architecture_summary()
    assert "graph" in summary
    assert "embeddings" in summary
    assert "last_indexed" in summary
