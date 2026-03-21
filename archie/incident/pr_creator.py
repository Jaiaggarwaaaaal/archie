"""Create GitHub PRs with fixes."""
import logging
from datetime import datetime
from github import Github
from git import Repo

from archie.incident.investigator import RootCause
from archie.incident.fix_generator import CodeFix

logger = logging.getLogger(__name__)


class PRCreator:
    """Creates GitHub pull requests with fixes."""
    
    def __init__(
        self,
        github_token: str,
        repo_owner: str,
        repo_name: str,
        local_repo_path: str
    ):
        self.gh = Github(github_token)
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.local_repo = Repo(local_repo_path)
        self.gh_repo = self.gh.get_repo(f"{repo_owner}/{repo_name}")
    
    def create_pr(
        self,
        incident_id: str,
        incident_title: str,
        root_cause: RootCause,
        fix: CodeFix
    ) -> str:
        """Create a PR with the fix."""
        logger.info(f"Creating PR for incident {incident_id}")
        
        # Step 1: Create branch
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"archie/fix-{incident_id}-{timestamp}"
        
        # Get current branch
        current_branch = self.local_repo.active_branch
        
        # Create new branch
        new_branch = self.local_repo.create_head(branch_name)
        new_branch.checkout()
        
        try:
            # Step 2: Apply fix
            with open(root_cause.responsible_file, "w") as f:
                f.write(fix.fixed_code)
            
            # Step 3: Commit
            self.local_repo.index.add([root_cause.responsible_file])
            commit_message = f"[Archie] Fix: {root_cause.root_cause[:72]}"
            self.local_repo.index.commit(commit_message)
            
            # Step 4: Push
            origin = self.local_repo.remote("origin")
            origin.push(refspec=f"{branch_name}:{branch_name}")
            
            # Step 5: Create PR
            pr_body = self._build_pr_body(
                incident_title,
                root_cause,
                fix
            )
            
            pr = self.gh_repo.create_pull(
                title=f"[Archie] Fix: {root_cause.root_cause[:72]}",
                body=pr_body,
                head=branch_name,
                base="main"
            )
            
            # Step 6: Add label
            try:
                pr.add_to_labels("archie-auto-fix")
            except Exception as e:
                logger.warning(f"Could not add label: {e}")
            
            logger.info(f"PR created: {pr.html_url}")
            return pr.html_url
            
        finally:
            # Return to original branch
            current_branch.checkout()

    def _build_pr_body(
        self,
        incident_title: str,
        root_cause: RootCause,
        fix: CodeFix
    ) -> str:
        """Build PR description."""
        
        affected_services_str = "\n".join([f"- {s}" for s in root_cause.affected_services])
        
        body = f"""## Archie Auto-Fix

**Incident:** {incident_title}

**Root cause:** {root_cause.root_cause}

**Confidence:** {root_cause.confidence_score}%

### What changed

{fix.change_summary}

### Files affected

- `{root_cause.responsible_file}` — lines {", ".join(map(str, fix.lines_changed))}

### Other services at risk

{affected_services_str if affected_services_str else "None identified"}

### Suggested regression test

{fix.test_suggestion}

### Reasoning

{root_cause.reasoning}

---

*This PR was opened automatically by Archie. Human review recommended before merging.*
"""
        return body
