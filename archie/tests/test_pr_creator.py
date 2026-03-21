"""Tests for the PR creator module."""
import pytest
from archie.incident.investigator import RootCause
from archie.incident.fix_generator import CodeFix


@pytest.fixture
def sample_root_cause():
    """Create a sample root cause."""
    return RootCause(
        root_cause="Missing null check on card.token",
        responsible_file="payment.py",
        responsible_function="process_payment",
        responsible_line=16,
        responsible_commit="abc123",
        confidence_score=85,
        affected_services=["payment-service"],
        reasoning="The code attempts to access card.token without checking if card is None"
    )


@pytest.fixture
def sample_fix():
    """Create a sample fix."""
    return CodeFix(
        fixed_code="# Fixed code here",
        change_summary="Added null check before accessing card.token",
        lines_changed=[16],
        confidence_score=90,
        test_suggestion="Add test for null card input"
    )


def test_build_pr_body(sample_root_cause, sample_fix):
    """Test building PR body."""
    from archie.incident.pr_creator import PRCreator
    
    # Create a mock PR creator (without actual GitHub connection)
    class MockPRCreator:
        def _build_pr_body(self, title, root_cause, fix):
            return PRCreator._build_pr_body(None, title, root_cause, fix)
    
    creator = MockPRCreator()
    body = creator._build_pr_body(
        "Test Incident",
        sample_root_cause,
        sample_fix
    )
    
    assert "Archie Auto-Fix" in body
    assert "Missing null check" in body
    assert "85%" in body
    assert "payment.py" in body
