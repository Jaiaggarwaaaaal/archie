"""Webhook listener for incident alerts."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import hmac
import hashlib
from fastapi import HTTPException


@dataclass
class IncidentContext:
    """Parsed incident context."""
    source: str
    title: str
    error_message: str
    stack_trace: Optional[str]
    affected_files: List[str]
    timestamp: datetime
    raw_payload: Dict


class IncidentParser:
    """Parse incident payloads from various sources."""
    
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def parse_sentry(self, payload: Dict) -> IncidentContext:
        """Parse Sentry webhook payload."""
        error_message = payload.get("message", "")
        title = payload.get("culprit", "Unknown error")
        
        # Extract stack trace
        stack_trace = None
        affected_files = []
        
        exception = payload.get("exception", {})
        if exception and "values" in exception:
            for exc in exception["values"]:
                if "stacktrace" in exc and "frames" in exc["stacktrace"]:
                    frames = exc["stacktrace"]["frames"]
                    stack_trace = "\n".join([
                        f"{f.get('filename', 'unknown')}:{f.get('lineno', 0)} in {f.get('function', 'unknown')}"
                        for f in frames
                    ])
                    affected_files = [f.get("filename", "") for f in frames if f.get("filename")]
        
        timestamp = datetime.fromisoformat(payload.get("timestamp", "").replace("Z", "+00:00"))
        
        return IncidentContext(
            source="sentry",
            title=title,
            error_message=error_message,
            stack_trace=stack_trace,
            affected_files=affected_files,
            timestamp=timestamp,
            raw_payload=payload
        )

    def parse_pagerduty(self, payload: Dict) -> IncidentContext:
        """Parse PagerDuty webhook payload."""
        messages = payload.get("messages", [])
        if not messages:
            raise ValueError("No messages in PagerDuty payload")
        
        incident = messages[0].get("incident", {})
        title = incident.get("title", "Unknown incident")
        service_name = incident.get("service", {}).get("name", "")
        
        error_message = f"High error rate on {service_name}" if service_name else title
        timestamp_str = incident.get("created_at", datetime.now().isoformat())
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        
        return IncidentContext(
            source="pagerduty",
            title=title,
            error_message=error_message,
            stack_trace=None,
            affected_files=[],
            timestamp=timestamp,
            raw_payload=payload
        )
    
    def parse_slack(self, payload: Dict) -> IncidentContext:
        """Parse Slack webhook payload."""
        event = payload.get("event", {})
        text = event.get("text", "")
        timestamp_str = event.get("ts", str(datetime.now().timestamp()))
        timestamp = datetime.fromtimestamp(float(timestamp_str))
        
        return IncidentContext(
            source="slack",
            title="Manual incident report",
            error_message=text,
            stack_trace=None,
            affected_files=[],
            timestamp=timestamp,
            raw_payload=payload
        )
    
    def parse_manual(self, payload: Dict) -> IncidentContext:
        """Parse manual incident payload."""
        title = payload.get("title", "Manual incident")
        error_message = payload.get("error_message", "")
        
        # Extract details
        details = payload.get("details", {})
        stack_trace = details.get("stack_trace") or payload.get("stack_trace")
        affected_files = details.get("affected_files", []) or payload.get("affected_files", [])
        
        # Parse timestamp
        timestamp_str = payload.get("timestamp", datetime.now().isoformat())
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except:
            timestamp = datetime.now()
        
        return IncidentContext(
            source="manual",
            title=title,
            error_message=error_message,
            stack_trace=stack_trace,
            affected_files=affected_files,
            timestamp=timestamp,
            raw_payload=payload
        )
    
    def parse(self, payload: Dict, source: Optional[str] = None) -> IncidentContext:
        """Parse incident payload based on source."""
        # Auto-detect source if not provided
        if source is None:
            # Check if source is explicitly provided in payload
            if "source" in payload:
                source = payload["source"]
            elif "exception" in payload or "culprit" in payload:
                source = "sentry"
            elif "messages" in payload and "incident" in payload.get("messages", [{}])[0]:
                source = "pagerduty"
            elif "event" in payload and payload["event"].get("type") == "message":
                source = "slack"
            else:
                raise ValueError("Could not detect incident source")
        
        if source == "sentry":
            return self.parse_sentry(payload)
        elif source == "pagerduty":
            return self.parse_pagerduty(payload)
        elif source == "slack":
            return self.parse_slack(payload)
        elif source == "manual":
            return self.parse_manual(payload)
        else:
            raise ValueError(f"Unknown source: {source}")
