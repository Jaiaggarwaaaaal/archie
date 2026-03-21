"""End-to-end integration tests."""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from archie.engine.indexer import CodeIndexer
from archie.incident.listener import IncidentParser


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for the database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_repo_path():
    return Path(__file__).parent / "fixtures" / "sample_repo"


@pytest.fixture
def indexer(temp_db_path):
    """Create an indexer."""
    return CodeIndexer(temp_db_path)


def test_full_indexing_pipeline(indexer, sample_repo_path):
    """Test the complete indexing pipeline."""
    # Index the sample repo
    indexer.index_repo(str(sample_repo_path))
    
    # Verify graph was built
    stats = indexer.graph.get_stats()
    assert stats["files"] > 0
    assert stats["functions"] > 0
    
    # Verify embeddings were created
    embedding_stats = indexer.embeddings.get_stats()
    assert embedding_stats["total_embeddings"] > 0
    
    # Test semantic search
    results = indexer.embeddings.search("payment validation")
    assert len(results) > 0
    
    # Test graph queries
    node = indexer.graph.get_node("process_payment")
    assert node is not None
    assert node["type"] == "function"


def test_incident_parsing_all_sources():
    """Test parsing all incident sources."""
    parser = IncidentParser("test_secret")
    fixtures_dir = Path(__file__).parent / "fixtures" / "incident_payloads"
    
    # Test Sentry
    with open(fixtures_dir / "sentry_payload.json") as f:
        sentry = json.load(f)
    incident = parser.parse(sentry)
    assert incident.source == "sentry"
    assert len(incident.affected_files) > 0
    
    # Test PagerDuty
    with open(fixtures_dir / "pagerduty_payload.json") as f:
        pagerduty = json.load(f)
    incident = parser.parse(pagerduty)
    assert incident.source == "pagerduty"
    
    # Test Slack
    with open(fixtures_dir / "slack_payload.json") as f:
        slack = json.load(f)
    incident = parser.parse(slack)
    assert incident.source == "slack"


def test_incremental_update_workflow(indexer, sample_repo_path):
    """Test incremental file updates."""
    # Initial index
    indexer.index_repo(str(sample_repo_path))
    initial_stats = indexer.graph.get_stats()
    
    # Update a single file
    file_path = str(sample_repo_path / "validators.py")
    indexer.update_file(file_path)
    
    # Stats should be similar (no duplicates)
    updated_stats = indexer.graph.get_stats()
    assert abs(updated_stats["total_nodes"] - initial_stats["total_nodes"]) < 5


def test_duplicate_detection(indexer, sample_repo_path):
    """Test finding duplicate functions."""
    indexer.index_repo(str(sample_repo_path))
    
    # Search for email validation - should find duplicates
    results = indexer.embeddings.find_duplicate("validate email address")
    
    # Should find both validate_email functions
    names = [r["name"] for r in results]
    assert names.count("validate_email") >= 2
