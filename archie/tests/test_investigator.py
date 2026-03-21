"""Tests for the investigator module."""
import pytest
import json
from pathlib import Path
from datetime import datetime
from archie.incident.listener import IncidentContext


@pytest.fixture
def sample_incident():
    """Create a sample incident."""
    return IncidentContext(
        source="sentry",
        title="payment.process_payment",
        error_message="AttributeError: 'NoneType' object has no attribute 'token'",
        stack_trace="payment.py:16 in process_payment",
        affected_files=["payment.py"],
        timestamp=datetime.now(),
        raw_payload={}
    )


@pytest.fixture
def sentry_payload():
    """Load Sentry payload fixture."""
    path = Path(__file__).parent / "fixtures" / "incident_payloads" / "sentry_payload.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def pagerduty_payload():
    """Load PagerDuty payload fixture."""
    path = Path(__file__).parent / "fixtures" / "incident_payloads" / "pagerduty_payload.json"
    with open(path) as f:
        return json.load(f)


def test_parse_sentry_payload(sentry_payload):
    """Test parsing Sentry payload."""
    from archie.incident.listener import IncidentParser
    
    parser = IncidentParser("test_secret")
    incident = parser.parse_sentry(sentry_payload)
    
    assert incident.source == "sentry"
    assert "AttributeError" in incident.error_message
    assert incident.stack_trace is not None
    assert len(incident.affected_files) > 0


def test_parse_pagerduty_payload(pagerduty_payload):
    """Test parsing PagerDuty payload."""
    from archie.incident.listener import IncidentParser
    
    parser = IncidentParser("test_secret")
    incident = parser.parse_pagerduty(pagerduty_payload)
    
    assert incident.source == "pagerduty"
    assert incident.title is not None


def test_auto_detect_source(sentry_payload):
    """Test auto-detecting incident source."""
    from archie.incident.listener import IncidentParser
    
    parser = IncidentParser("test_secret")
    incident = parser.parse(sentry_payload)
    
    assert incident.source == "sentry"
