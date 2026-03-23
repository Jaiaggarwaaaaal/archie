# Troubleshooting Guide

## Installation Issues

### "No module named tree_sitter"
```bash
pip install py-tree-sitter tree-sitter-python tree-sitter-javascript
```

### "No module named lancedb"
```bash
pip install lancedb sentence-transformers
```

### Python version issues
Archie requires Python 3.11+. Check your version:
```bash
python3 --version
```

## Runtime Issues

### "Indexer not initialized"
The services haven't started. Make sure:
1. `.env` file exists with all required variables
2. Server started successfully (check logs)
3. `/index/trigger` was called to initialize

### "Could not parse file"
- Check file extension is .py, .js, or .ts
- Verify file has valid syntax
- Check file permissions

### "LanceDB connection error"
- Ensure `LANCEDB_PATH` directory is writable
- Check disk space
- Try deleting `.lancedb` directory and re-indexing

### "Graph has no nodes"
- Run `/index/trigger` to index the codebase first
- Check `REPO_PATH` points to correct directory
- Verify directory contains .py or .js files

## Webhook Issues

### "Invalid signature"
- Verify `WEBHOOK_SECRET` matches webhook configuration
- Check `X-Signature` header is being sent
- Ensure webhook is sending raw body (not JSON parsed)

### "Could not detect incident source"
- Check payload format matches Sentry/PagerDuty/Slack
- Try specifying source explicitly in request
- Verify JSON is valid

### "No affected files found"
- Sentry: Check stack trace includes file paths
- PagerDuty: Service name should match codebase
- Slack: Message should mention file names

## Claude API Issues

### "Anthropic API error"
- Verify `ANTHROPIC_API_KEY` is correct
- Check API quota/limits
- Ensure model name is correct: `claude-sonnet-4-20250514`

### "Could not parse Claude response"
- Claude sometimes returns markdown code blocks
- Parser handles this automatically
- Check logs for actual response

### "Low confidence scores"
- Not enough context in graph
- Recent changes not captured
- Try re-indexing codebase

## GitHub Issues

### "GitHub authentication failed"
- Verify `GITHUB_TOKEN` has correct permissions
- Token needs: `repo` scope (full control)
- Check token hasn't expired

### "Could not create branch"
- Ensure local repo is clean (no uncommitted changes)
- Check you're on a valid branch
- Verify remote is accessible

### "Could not push branch"
- Check network connectivity
- Verify GitHub token has push access
- Ensure branch name doesn't already exist

### "Could not create PR"
- Base branch must exist (usually `main` or `master`)
- Check if PR already exists for this branch
- Verify repo settings allow PRs

## Performance Issues

### "Indexing is slow"
- Large repos take time (1-2s per 100 files)
- Skip unnecessary directories in watcher
- Consider indexing only specific subdirectories

### "High memory usage"
- Graph stores all nodes in memory
- Embeddings model loads into RAM (~100MB)
- Consider splitting very large repos

### "Semantic search returns no results"
- Embeddings might not be created
- Check `/index/status` shows embeddings count > 0
- Try re-indexing

## Git Issues

### "No recent commits found"
- Check git history exists
- Verify commits are within 48 hour window
- Ensure `.git` directory is accessible

### "Could not get diff"
- Some commits have no parents (initial commit)
- Parser handles this gracefully
- Check git repo is valid

## Common Mistakes

### Forgetting to index
Always run `/index/trigger` after starting server:
```bash
curl -X POST http://localhost:8000/index/trigger
```

### Wrong repo path
`REPO_PATH` must be absolute path:
```
REPO_PATH=/Users/you/projects/myapp  # ✅ Good
REPO_PATH=./myapp                     # ❌ Bad
```

### Missing environment variables
All variables in `.env.example` are required. Check:
```bash
cat .env
```

### Webhook secret mismatch
Secret in `.env` must match webhook configuration in Sentry/PagerDuty.

## Debug Mode

Enable debug logging:
```
LOG_LEVEL=DEBUG
```

Check logs for detailed information:
```bash
tail -f archie.log
```

## Getting Help

1. Check logs first
2. Verify configuration
3. Try example_usage.py to test components
4. Run tests: `pytest tests/ -v`
5. Check GitHub issues

## Testing Components Individually

### Test parser
```python
from archie.engine.parser import CodeParser
parser = CodeParser()
result = parser.parse_file("your_file.py")
print(result)
```

### Test graph
```python
from archie.engine.graph import CodeGraph
graph = CodeGraph()
# ... add files ...
print(graph.get_stats())
```

### Test embeddings
```python
from archie.engine.embeddings import EmbeddingsStore
store = EmbeddingsStore("./.test_db")
# ... embed nodes ...
results = store.search("your query")
print(results)
```

### Test incident parsing
```python
from archie.incident.listener import IncidentParser
parser = IncidentParser("secret")
incident = parser.parse(your_payload)
print(incident)
```
