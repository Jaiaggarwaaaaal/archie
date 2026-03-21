"""Root cause investigation engine."""
from dataclasses import dataclass
from typing import List, Optional, Dict
import logging
from datetime import datetime, timedelta
import asyncio
from git import Repo

from archie.incident.listener import IncidentContext
from archie.engine.graph import CodeGraph
from archie.engine.embeddings import EmbeddingsStore
from archie.engine.ai_provider import AIProvider, parse_json_response

logger = logging.getLogger(__name__)


@dataclass
class RootCause:
    """Root cause analysis result."""
    root_cause: str
    responsible_file: str
    responsible_function: str
    responsible_line: int
    responsible_commit: Optional[str]
    confidence_score: int
    affected_services: List[str]
    reasoning: str


class IncidentInvestigator:
    """Investigates incidents to find root cause."""
    
    def __init__(
        self,
        graph: CodeGraph,
        embeddings: EmbeddingsStore,
        repo_path: str,
        ai_provider: AIProvider
    ):
        self.graph = graph
        self.embeddings = embeddings
        self.repo_path = repo_path
        self.ai_provider = ai_provider
        self.repo = Repo(repo_path)
    
    async def investigate(self, incident: IncidentContext) -> RootCause:
        """Investigate an incident and find root cause."""
        logger.info(f"Investigating incident: {incident.title}")
        
        # Step 1: Find recent changes (run in executor - git operations)
        loop = asyncio.get_event_loop()
        recent_changes = await loop.run_in_executor(None, self._get_recent_changes, 48)
        
        # Step 2: Graph traversal (fast, in-memory)
        subgraph_data = self._build_subgraph(incident)
        
        # Step 3: Semantic search (fast, local)
        similar_nodes = self._find_similar_code(incident)
        
        # Step 4: AI reasoning (async API call)
        root_cause = await self._analyze_with_ai(
            incident,
            recent_changes,
            subgraph_data,
            similar_nodes
        )
        
        return root_cause

    def _get_recent_changes(self, hours: int = 48) -> List[Dict]:
        """Get recent commits and their diffs."""
        since = datetime.now() - timedelta(hours=hours)
        commits = list(self.repo.iter_commits(since=since.isoformat()))
        
        changes = []
        for commit in commits[:10]:  # Limit to 10 most recent
            try:
                diff = commit.diff(commit.parents[0] if commit.parents else None)
                changed_files = [d.a_path for d in diff if d.a_path]
                
                changes.append({
                    "sha": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "timestamp": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    "changed_files": changed_files,
                    "diff": commit.diff(commit.parents[0] if commit.parents else None, create_patch=True)
                })
            except Exception as e:
                logger.warning(f"Error processing commit {commit.hexsha}: {e}")
        
        return changes
    
    def _build_subgraph(self, incident: IncidentContext) -> Dict:
        """Build subgraph around affected code."""
        subgraph_data = {"nodes": [], "edges": []}
        
        for file_path in incident.affected_files:
            # Find functions in this file
            file_node_id = f"file:{file_path}"
            if self.graph.graph.has_node(file_node_id):
                subgraph = self.graph.subgraph_around(file_node_id, depth=2)
                subgraph_data["nodes"].extend(subgraph["nodes"])
                subgraph_data["edges"].extend(subgraph["edges"])
        
        # Deduplicate
        seen_nodes = set()
        unique_nodes = []
        for node in subgraph_data["nodes"]:
            if node["id"] not in seen_nodes:
                seen_nodes.add(node["id"])
                unique_nodes.append(node)
        subgraph_data["nodes"] = unique_nodes
        
        return subgraph_data
    
    def _find_similar_code(self, incident: IncidentContext) -> List[Dict]:
        """Find semantically similar code."""
        query = f"{incident.error_message} {incident.title}"
        return self.embeddings.search(query, top_k=5)

    async def _analyze_with_ai(
        self,
        incident: IncidentContext,
        recent_changes: List[Dict],
        subgraph: Dict,
        similar_nodes: List[Dict]
    ) -> RootCause:
        """Use AI to analyze and find root cause."""
        import json
        
        # Build prompt
        prompt = f"""You are an expert staff engineer investigating a production incident.

INCIDENT:
Source: {incident.source}
Title: {incident.title}
Error: {incident.error_message}
Stack Trace:
{incident.stack_trace or "N/A"}
Affected Files: {", ".join(incident.affected_files)}
Timestamp: {incident.timestamp.isoformat()}

RECENT CODE CHANGES (last 48 hours):
{json.dumps(recent_changes, indent=2, default=str)[:2000]}

AFFECTED CODEBASE SUBGRAPH:
{json.dumps(subgraph, indent=2)[:2000]}

SEMANTICALLY SIMILAR CODE:
{json.dumps(similar_nodes, indent=2)[:1000]}

Respond with JSON only:
{{
  "root_cause": "clear explanation of what caused this",
  "responsible_file": "path/to/file.py",
  "responsible_function": "function_name",
  "responsible_line": 42,
  "responsible_commit": "commit_sha or null",
  "confidence_score": 85,
  "affected_services": ["list of other services at risk"],
  "reasoning": "step by step explanation"
}}"""
        
        # Use AI provider (async)
        response_text = await self.ai_provider.generate(prompt, max_tokens=1000)
        
        # Parse response
        result = parse_json_response(response_text)
        
        return RootCause(**result)
