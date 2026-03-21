# Archie — AI Staff Engineer Agent

Archie is a persistent AI agent that lives inside a codebase and acts as a staff engineer.

## Current Status: Mode 3 (Incident Agent) - COMPLETE ✅

### Architecture

Archie consists of three main subsystems:

1. **Engine** - Core intelligence layer
   - `parser.py` - Tree-sitter AST parser for Python/JavaScript
   - `graph.py` - NetworkX knowledge graph of codebase structure
   - `embeddings.py` - LanceDB vector store with semantic search
   - `indexer.py` - Orchestrates parsing, graph building, and embedding
   - `watcher.py` - File system watcher for incremental updates

2. **Incident** - Automated incident response
   - `listener.py` - Webhook parser for Sentry/PagerDuty/Slack
   - `investigator.py` - Root cause analysis using graph + Claude API
   - `fix_generator.py` - Generates code fixes via Claude API
   - `pr_creator.py` - Opens GitHub PRs with fixes

3. **API** - FastAPI server
   - Health checks, indexing status, semantic search
   - Webhook endpoint for incident alerts

## Installation

```bash
cd archie
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Fill in your credentials:
```
# Choose AI provider: "openai" or "anthropic"
AI_PROVIDER=openai

# Provide the API key for your chosen provider
OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: customize models
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# GitHub configuration
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo
REPO_PATH=/absolute/path/to/your/codebase
WEBHOOK_SECRET=your_webhook_secret
```

### AI Provider Options

Archie supports two AI providers:

**OpenAI (Default)**
- Set `AI_PROVIDER=openai`
- Provide `OPENAI_API_KEY`
- Default model: `gpt-4o`
- Also supports: `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`

**Anthropic Claude**
- Set `AI_PROVIDER=anthropic`
- Provide `ANTHROPIC_API_KEY`
- Default model: `claude-sonnet-4-20250514`
- Also supports: `claude-3-opus`, `claude-3-sonnet`

## Usage

### 1. Start the server

```bash
python -m archie.main
```

The server will start on `http://localhost:8000`

### 2. Index your codebase

```bash
curl -X POST http://localhost:8000/index/trigger
```

### 3. Set up webhooks

Configure your monitoring tools to send alerts to:
```
POST http://your-server:8000/webhook/incident
```

Supported sources:
- Sentry
- PagerDuty  
- Slack

### 4. When an incident occurs

Archie will automatically:
1. Parse the incident alert
2. Analyze recent code changes (last 48 hours)
3. Traverse the knowledge graph to find affected code
4. Use semantic search to find similar patterns
5. Ask Claude API to identify root cause
6. Generate a minimal fix
7. Open a GitHub PR with the fix

## API Endpoints

- `GET /health` - Health check
- `GET /index/status` - Get indexing statistics
- `POST /index/trigger` - Manually trigger full re-index
- `GET /graph/summary` - Get architecture summary
- `GET /graph/node/{name}` - Get node details
- `POST /search` - Semantic search: `{"query": "your search"}`
- `POST /webhook/incident` - Receive incident alerts

### Graph Visualization (New!)

- `GET /graph/visualize` - Get graph data as JSON (for D3.js, Cytoscape, etc.)
- `GET /graph/mermaid` - Get Mermaid diagram syntax
- `GET /graph/mermaid/view` - View interactive Mermaid diagram in browser
- `GET /graph/3d` - **View interactive 3D graph (recommended!)**
- `GET /graph/file/{file_path}/dependencies` - Get all dependencies for a file
- `GET /graph/analysis/circular` - Find circular dependencies
- `GET /graph/analysis/hotspots` - Find most connected nodes (hotspots)

### Example: View Graph in Browser

```bash
# 🌟 View 3D interactive graph (BEST!)
open http://localhost:8000/graph/3d

# Filter 3D graph by file pattern
open http://localhost:8000/graph/3d?file_filter=payment&max_nodes=100

# View 2D Mermaid diagram
open http://localhost:8000/graph/mermaid/view

# View specific file's dependencies
open http://localhost:8000/graph/mermaid/view?file_path=src/payment.py&depth=2

# Get file dependencies as JSON
curl http://localhost:8000/graph/file/src/payment.py/dependencies

# Find circular dependencies
curl http://localhost:8000/graph/analysis/circular

# Find hotspots (most connected code)
curl http://localhost:8000/graph/analysis/hotspots
```

### 3D Graph Features

- 🎮 **Interactive** - Drag to rotate, scroll to zoom
- 🎨 **Color-coded** - Files (blue), Functions (orange), Classes (purple)
- 🔗 **Animated edges** - See function calls flow
- 👆 **Click nodes** - View detailed information
- 🔍 **Filter** - Focus on specific files or modules
- 📊 **Real-time stats** - Node counts and connections

## Running Tests

```bash
pytest tests/ -v
```

## How It Works

### Incident Flow

1. **Alert Received** → Webhook parses Sentry/PagerDuty/Slack payload
2. **Investigation** → 
   - Git analysis: Find commits in last 48 hours
   - Graph traversal: Build subgraph around affected files
   - Semantic search: Find similar code patterns
3. **Root Cause Analysis** → Claude API analyzes all context
4. **Fix Generation** → Claude generates minimal fix with validation
5. **PR Creation** → Automated PR with explanation and confidence score

### Key Features

- **Incremental indexing** - Only re-parses changed files
- **Semantic search** - Find code by meaning, not just text
- **Graph-based analysis** - Understand dependencies and call chains
- **Confidence scores** - Every fix includes confidence percentage
- **Signature validation** - Ensures fixes don't break existing APIs

## Next Steps (Future Modes)

- **Mode 1: Onboarding** - Explain system to new engineers
- **Mode 2: Build Mode** - Catch wrong paths, duplicates before commit

## License

MIT
