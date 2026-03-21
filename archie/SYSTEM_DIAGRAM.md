# Archie System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ARCHIE SYSTEM                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL TRIGGERS                               │
├─────────────────────────────────────────────────────────────────────┤
│  Sentry Alert    PagerDuty Alert    Slack Message                   │
│       │                 │                  │                         │
│       └─────────────────┴──────────────────┘                         │
│                          │                                           │
│                          ▼                                           │
│              POST /webhook/incident                                  │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INCIDENT LISTENER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  • Verify webhook signature                                          │
│  • Parse payload (Sentry/PagerDuty/Slack)                           │
│  • Extract: error, stack trace, affected files                      │
│  • Create IncidentContext                                            │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   INCIDENT INVESTIGATOR                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Step 1: GIT ANALYSIS                                                │
│  ┌────────────────────────────────────┐                             │
│  │ • Get commits (last 48 hours)      │                             │
│  │ • Extract diffs                    │                             │
│  │ • Find changed files               │                             │
│  └────────────────────────────────────┘                             │
│                                                                       │
│  Step 2: GRAPH TRAVERSAL                                             │
│  ┌────────────────────────────────────┐                             │
│  │ • Find affected file nodes         │                             │
│  │ • Build subgraph (depth=2)         │                             │
│  │ • Get callers & callees            │                             │
│  │ • Map dependencies                 │                             │
│  └────────────────────────────────────┘                             │
│                                                                       │
│  Step 3: SEMANTIC SEARCH                                             │
│  ┌────────────────────────────────────┐                             │
│  │ • Query embeddings store           │                             │
│  │ • Find similar functions           │                             │
│  │ • Identify patterns                │                             │
│  └────────────────────────────────────┘                             │
│                                                                       │
│  Step 4: CLAUDE API ANALYSIS                                         │
│  ┌────────────────────────────────────┐                             │
│  │ • Send context to Claude           │                             │
│  │ • Get root cause analysis          │                             │
│  │ • Extract confidence score         │                             │
│  └────────────────────────────────────┘                             │
│                                                                       │
│  Output: RootCause                                                   │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FIX GENERATOR                                    │
├─────────────────────────────────────────────────────────────────────┤
│  • Read broken file content                                          │
│  • Get subgraph context                                              │
│  • Send to Claude API                                                │
│  • Generate minimal fix                                              │
│  • Validate function signatures                                      │
│  • Output: CodeFix                                                   │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PR CREATOR                                      │
├─────────────────────────────────────────────────────────────────────┤
│  1. Create branch: archie/fix-{id}-{timestamp}                      │
│  2. Apply fix to file                                                │
│  3. Commit: "[Archie] Fix: {root_cause}"                            │
│  4. Push to GitHub                                                   │
│  5. Open PR with detailed description                                │
│  6. Add label: "archie-auto-fix"                                    │
│                                                                       │
│  Output: PR URL                                                      │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ✅ PR Created!


═══════════════════════════════════════════════════════════════════════
                        CORE ENGINE LAYER
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                         CODEBASE                                     │
│                    (Python, JS, TS files)                            │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PARSER                                       │
│                    (Tree-sitter AST)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Extracts:                                                           │
│  • Functions (name, params, lines)                                   │
│  • Classes (name, methods)                                           │
│  • Imports (module, names)                                           │
│  • Calls (caller → callee)                                          │
└─────────────────────────────────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│    KNOWLEDGE GRAPH       │  │   EMBEDDINGS STORE       │
│      (NetworkX)          │  │     (LanceDB)            │
├──────────────────────────┤  ├──────────────────────────┤
│ Nodes:                   │  │ • Sentence transformers  │
│  • Files                 │  │ • Vector search          │
│  • Functions             │  │ • Semantic similarity    │
│  • Classes               │  │ • Duplicate detection    │
│                          │  │                          │
│ Edges:                   │  │ Indexed:                 │
│  • calls                 │  │  • Function names        │
│  • imports               │  │  • Docstrings            │
│  • contains              │  │  • Parameters            │
│  • depends_on            │  │                          │
│                          │  │                          │
│ Operations:              │  │ Operations:              │
│  • get_callers()         │  │  • search()              │
│  • get_callees()         │  │  • find_duplicate()      │
│  • subgraph_around()     │  │                          │
│  • find_similar_nodes()  │  │                          │
└──────────────────────────┘  └──────────────────────────┘
                │                        │
                └────────────┬───────────┘
                             ▼
                    ┌─────────────────┐
                    │    INDEXER      │
                    ├─────────────────┤
                    │ • Orchestrates  │
                    │ • Full index    │
                    │ • Incremental   │
                    └─────────────────┘
                             ▲
                             │
                    ┌─────────────────┐
                    │    WATCHER      │
                    ├─────────────────┤
                    │ • File monitor  │
                    │ • Auto-update   │
                    └─────────────────┘


═══════════════════════════════════════════════════════════════════════
                           API LAYER
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Server                                  │
│                     (localhost:8000)                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  GET  /health              → Health check                            │
│  GET  /index/status        → Graph & embedding stats                │
│  POST /index/trigger       → Full re-index                           │
│  GET  /graph/summary       → Architecture overview                   │
│  GET  /graph/node/{name}   → Node details                            │
│  POST /search              → Semantic search                         │
│  POST /webhook/incident    → Incident webhook (MAIN)                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                        DATA PERSISTENCE
═══════════════════════════════════════════════════════════════════════

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  .lancedb/       │  │  .graph.pkl      │  │  Git Repo        │
│  (Vector Store)  │  │  (Graph Pickle)  │  │  (Source Code)   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Key Flows

### 1. Initial Setup
```
Start Server → Initialize Services → Index Repo → Ready
```

### 2. File Change
```
File Modified → Watcher Detects → Indexer Updates → Graph + Embeddings Updated
```

### 3. Incident Response
```
Alert → Parse → Investigate → Generate Fix → Create PR → Done
```

### 4. Manual Query
```
API Request → Query Graph/Embeddings → Return Results
```
