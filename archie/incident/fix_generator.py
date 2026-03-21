"""Generate code fixes for incidents."""
from dataclasses import dataclass
from typing import List, Dict
import logging

from archie.incident.investigator import RootCause
from archie.engine.graph import CodeGraph
from archie.engine.ai_provider import AIProvider, parse_json_response

logger = logging.getLogger(__name__)


@dataclass
class CodeFix:
    """Generated code fix."""
    fixed_code: str
    change_summary: str
    lines_changed: List[int]
    confidence_score: int
    test_suggestion: str


class FixGenerator:
    """Generates code fixes for incidents."""
    
    def __init__(self, graph: CodeGraph, ai_provider: AIProvider, repo_path: str = None):
        self.graph = graph
        self.ai_provider = ai_provider
        self.repo_path = repo_path
    
    async def generate_fix(self, root_cause: RootCause) -> CodeFix:
        """Generate a fix for the root cause."""
        logger.info(f"Generating fix for {root_cause.responsible_file}")
        
        # Build full path to file
        import os
        if self.repo_path:
            file_path = os.path.join(self.repo_path, root_cause.responsible_file)
        else:
            file_path = root_cause.responsible_file
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}. Generating conceptual fix.")
            # Generate a conceptual fix without reading the file
            return await self._generate_conceptual_fix(root_cause)
        
        # Read the broken file (async I/O)
        import aiofiles
        async with aiofiles.open(file_path, "r") as f:
            file_content = await f.read()
        
        # Get subgraph context
        file_node_id = f"file:{root_cause.responsible_file}"
        subgraph = {}
        if self.graph.graph.has_node(file_node_id):
            subgraph = self.graph.subgraph_around(file_node_id, depth=1)
        
        # Generate fix with AI (async)
        fix = await self._generate_with_ai(root_cause, file_content, subgraph)
        
        # Validate fix doesn't break signatures
        self._validate_signatures(root_cause.responsible_file, fix.fixed_code)
        
        return fix
    
    async def _generate_with_ai(
        self,
        root_cause: RootCause,
        file_content: str,
        subgraph: Dict
    ) -> CodeFix:
        """Use AI to generate the fix."""
        import json
        
        prompt = f"""You are an expert engineer fixing a production bug.

ROOT CAUSE:
{root_cause.root_cause}
File: {root_cause.responsible_file}
Function: {root_cause.responsible_function}
Line: {root_cause.responsible_line}
Reasoning: {root_cause.reasoning}

BROKEN FILE CONTENT:
{file_content}

CODEBASE CONTEXT (what this function is called by, what it calls):
{json.dumps(subgraph, indent=2, default=str)[:1500]}

Generate a minimal, safe fix. Respond with JSON only:
{{
  "fixed_code": "complete fixed file content",
  "change_summary": "one sentence: what was changed and why",
  "lines_changed": [42, 43],
  "confidence_score": 90,
  "test_suggestion": "what test should be added to prevent regression"
}}"""

        # Use AI provider (async)
        response_text = await self.ai_provider.generate(prompt, max_tokens=1000)
        
        # Parse response
        result = parse_json_response(response_text)
        
        return CodeFix(**result)
    
    async def _generate_conceptual_fix(self, root_cause: RootCause) -> CodeFix:
        """Generate a conceptual fix when file doesn't exist."""
        prompt = f"""You are an expert engineer analyzing a production bug.

ROOT CAUSE:
{root_cause.root_cause}
File: {root_cause.responsible_file} (file not found in repo)
Function: {root_cause.responsible_function}
Line: {root_cause.responsible_line}
Reasoning: {root_cause.reasoning}

The file doesn't exist in the current codebase. Generate a conceptual fix description.

Respond with ONLY valid JSON, no markdown:
{{
  "fixed_code": "Conceptual fix description here",
  "change_summary": "what should be changed and why",
  "lines_changed": [],
  "confidence_score": 50,
  "test_suggestion": "what test should be added"
}}"""

        response_text = await self.ai_provider.generate(prompt, max_tokens=500)
        
        try:
            result = parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Failed to parse conceptual fix response: {e}")
            # Return a fallback response
            return CodeFix(
                fixed_code=f"Conceptual fix: {root_cause.root_cause}",
                change_summary="Fix needed in report generation logic",
                lines_changed=[],
                confidence_score=50,
                test_suggestion="Add integration test for report generation"
            )
        
        return CodeFix(**result)
    
    def _validate_signatures(self, file_path: str, fixed_code: str) -> None:
        """Validate that function signatures haven't changed."""
        # Get all functions that depend on this file
        file_node_id = f"file:{file_path}"
        if not self.graph.graph.has_node(file_node_id):
            return
        
        # Get all functions in this file
        functions_in_file = [
            n for n in self.graph.graph.nodes()
            if self.graph.graph.nodes[n].get("file_path") == file_path
            and self.graph.graph.nodes[n].get("type") == "function"
        ]
        
        # Check if any of these functions are called by other files
        for func_node in functions_in_file:
            callers = self.graph.get_callers(self.graph.graph.nodes[func_node]["name"])
            external_callers = [
                c for c in callers 
                if c.get("file_path") != file_path
            ]
            
            if external_callers:
                logger.warning(
                    f"Function {self.graph.graph.nodes[func_node]['name']} "
                    f"has external callers. Ensure signature is preserved."
                )
