# Archie Architecture

## Overview

Archie is an AI staff engineer agent that automatically investigates production incidents and opens fix PRs. It consists of three main subsystems working together.

## System Components

### 1. Engine Layer (Core Intelligence)

#### parser.py
- Uses tree-sitter for AST parsing
- Supports Python and JavaScript/TypeScript
- Extracts: functions, classes, imports, function calls
- Output: Structured dict with all code elements

#### graph.py
- NetworkX directed graph
- Nodes: files, functions, classes (with metadata)
- Edges: calls, imports, contains, depends_on
- Key operations:
  - `get_callers()` - Find what calls a function
  - `get_callees()` - Find what a function calls
  - `subgraph_around()` - Get context around a node
  - `find_similar_nodes()` - Fuzzy name matching

#### embeddings.py
- LanceDB vector store (local, no server)
- sentence-transformers (all-MiniLM-L6-v2)
- Embeds function names + docstrings + parameters
- Semantic search for similar code
- Duplicate detection

#### indexer.py
- Orchestrates parser + graph + embeddings
- Full repo indexing: walks directory, parses all files
- Incremental updates: single file re-parsing
- No duplicates: removes old nodes before adding new

#### watcher.py
- Watchdog file system observer
- Monitors .py, .js, .ts files
- Triggers incremental updates on file changes
- Skips node_modules, .git, etc.

### 2. Incident Layer (Automated Response)

#### listener.py
- Parses webhooks from Sentry, PagerDuty, Slack
- Extracts: error message, stack trace, affected files
- Signature verification (HMAC-SHA256)
- Auto-detects source from payload structure

#### investigator.py
- Root cause analysis engine
- Four-step process:
  1. Git analysis: Find commits in last 48 hours
  2. Graph traversal: Build subgraph around affected files
  3. Semantic search: Find similar code patterns
  4. Claude API: Analyze all context and identify root cause
- Returns: RootCause with confidence score

#### fix_generator.py
- Generates code fixes via Claude API
- Validates function signatures aren't broken
- Returns: CodeFix with confidence score
- Includes test suggestions

#### pr_creator.py
- Creates GitHub branch
- Applies fix
- Commits and pushes
- Opens PR with detailed description
- Adds "archie-auto-fix" label

### 3. API Layer (FastAPI Server)

#### routes.py
- `/health` - Health check
- `/index/status` - Indexing statistics
- `/index/trigger` - Manual re-index
- `/graph/summary` - Architecture overview
- `/graph/node/{name}` - Node details
- `/search` - Semantic search
- `/webhook/incident` - Incident webhook (main entry point)

#### main.py
- FastAPI application
- Initializes all services on startup
- Runs on port 8000

## Data Flow

### Indexing Flow
```
Code Files → Parser → Graph + Embeddings → Persistent Storage
                ↓
         Watcher monitors changes
                ↓
         Incremental updates
```

### Incident Flow
```
Alert → Webhook → Parse Incident
                      ↓
                 Investigate:
                 - Git history
                 - Graph traversal
                 - Semantic search
                 - Claude analysis
                      ↓
                 Generate Fix:
                 - Claude API
                 - Signature validation
                      ↓
                 Create PR:
                 - Branch
                 - Commit
                 - Push
                 - Open PR
```

## Key Design Decisions

### 1. Incremental Updates
- Never full re-index on file change
- Remove old nodes, add new ones
- Prevents duplicate nodes in graph

### 2. Subgraph Context
- Claude receives relevant subgraph only
- Not entire codebase
- Reduces token usage, improves accuracy

### 3. Confidence Scores
- Every root cause has confidence %
- Every fix has confidence %
- Humans can prioritize reviews

### 4. Signature Validation
- Checks if functions are called externally
- Warns if signature might break
- Prevents cascading failures

### 5. Local-First
- LanceDB runs locally (no server)
- Embeddings generated locally
- Only Claude API is external

## Configuration

All settings via environment variables (pydantic BaseSettings):
- `ANTHROPIC_API_KEY` - Claude API
- `GITHUB_TOKEN` - GitHub API
- `REPO_PATH` - Local codebase path
- `WEBHOOK_SECRET` - Webhook verification
- `LANCEDB_PATH` - Vector store location
- `GRAPH_PERSIST_PATH` - Graph pickle location

## Testing Strategy

- Unit tests for each module
- Integration tests for full pipeline
- Fixture-based testing (sample repo + incident payloads)
- No mocks for core logic (test real behavior)

## Performance Characteristics

- Initial indexing: ~1-2 seconds per 100 files
- Incremental update: ~50-100ms per file
- Semantic search: ~10-50ms
- Graph traversal: ~1-5ms
- Claude API call: ~2-5 seconds
- Total incident response: ~10-20 seconds

## Future Enhancements

### Mode 1: Onboarding
- Explain codebase to new engineers
- Generate architecture diagrams
- Answer "how does X work?"

### Mode 2: Build Mode
- Pre-commit hooks
- Detect wrong module paths
- Find duplicate code
- Suggest better locations for new code

## Security Considerations

- Webhook signature verification required
- GitHub token needs PR write access
- Claude API key must be kept secret
- Local file system access required
- No data sent to external services except Claude API
