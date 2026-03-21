# Async Architecture in Archie

## Overview

Archie now uses **async/await throughout** for better performance, scalability, and non-blocking I/O operations.

## Why Async?

### Benefits

1. **Concurrent Request Handling**
   - Handle multiple incidents simultaneously
   - No blocking while waiting for AI API responses
   - Better resource utilization

2. **Non-Blocking I/O**
   - File operations don't block event loop
   - Git operations run in executor
   - API calls are truly async

3. **Better Scalability**
   - Can handle more requests with same resources
   - Efficient use of CPU and I/O
   - Lower latency under load

4. **Consistent Architecture**
   - Async from API layer down to AI providers
   - Clean async/await patterns
   - No sync/async mixing issues

## Architecture Layers

### 1. API Layer (FastAPI) - Fully Async

```python
@router.post("/webhook/incident")
async def webhook_incident(request: Request):
    # All operations are async
    incident = incident_parser.parse(payload)
    root_cause = await investigator.investigate(incident)  # Async
    fix = await fix_generator.generate_fix(root_cause)     # Async
    pr_url = await create_pr_async(...)                    # Async
    return {"pr_url": pr_url}
```

### 2. Engine Layer - Hybrid Async

**Async Operations:**
- `indexer.index_repo()` - Async with executor for CPU work
- `indexer.update_file()` - Async wrapper

**Sync Operations (run in executor):**
- `parser.parse_file()` - CPU-bound (tree-sitter)
- `graph.add_file()` - In-memory (fast)
- `embeddings.embed_node()` - CPU-bound (transformers)

```python
# Async wrapper for CPU-bound work
async def index_repo(self, repo_path: str):
    loop = asyncio.get_event_loop()
    for file_path in files:
        # Run CPU-bound work in thread pool
        await loop.run_in_executor(None, self._update_file_sync, file_path)
```

### 3. Incident Layer - Fully Async

**Investigator:**
```python
async def investigate(self, incident: IncidentContext) -> RootCause:
    # Git operations in executor
    recent_changes = await loop.run_in_executor(None, self._get_recent_changes)
    
    # Graph/embeddings (fast, sync)
    subgraph = self._build_subgraph(incident)
    similar = self._find_similar_code(incident)
    
    # AI API call (async)
    root_cause = await self._analyze_with_ai(...)
    return root_cause
```

**Fix Generator:**
```python
async def generate_fix(self, root_cause: RootCause) -> CodeFix:
    # File I/O (could be async, but fast enough)
    file_content = read_file(...)
    
    # AI API call (async)
    fix = await self._generate_with_ai(...)
    return fix
```

### 4. AI Provider Layer - Fully Async

```python
class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        # Use AsyncOpenAI client
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, max_tokens: int) -> str:
        # Async API call
        response = await self.client.chat.completions.create(...)
        return response.choices[0].message.content
```

## Async Patterns Used

### 1. Async/Await

```python
async def my_function():
    result = await some_async_operation()
    return result
```

### 2. Run in Executor (for CPU-bound work)

```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, cpu_bound_function, arg1, arg2)
```

### 3. Async Context Managers

```python
async with aiofiles.open('file.txt', 'r') as f:
    content = await f.read()
```

### 4. Concurrent Execution

```python
# Run multiple operations concurrently
results = await asyncio.gather(
    operation1(),
    operation2(),
    operation3()
)
```

## Performance Comparison

### Before (Sync)

```
Request 1: Parse → Graph → AI → PR (10s total)
Request 2: Waits...
Request 3: Waits...

Total time for 3 requests: 30 seconds
```

### After (Async)

```
Request 1: Parse → Graph → AI (waiting) → PR
Request 2: Parse → Graph → AI (waiting) → PR
Request 3: Parse → Graph → AI (waiting) → PR

Total time for 3 requests: ~12 seconds (concurrent AI calls)
```

## What Runs Where

### Event Loop (Non-Blocking)
- FastAPI request handling
- AI API calls (OpenAI/Anthropic)
- Async I/O operations
- Coordination logic

### Thread Pool Executor (CPU-Bound)
- Tree-sitter parsing
- Sentence transformer embeddings
- Git operations
- File I/O (when needed)

### Main Thread (Fast Operations)
- NetworkX graph operations (in-memory)
- LanceDB queries (local)
- JSON parsing
- Data transformations

## Best Practices

### 1. Always Await Async Functions

```python
# ✅ Good
result = await async_function()

# ❌ Bad
result = async_function()  # Returns coroutine, not result
```

### 2. Use Executor for CPU-Bound Work

```python
# ✅ Good
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, cpu_intensive_function)

# ❌ Bad
result = cpu_intensive_function()  # Blocks event loop
```

### 3. Don't Mix Sync and Async

```python
# ✅ Good
async def process():
    data = await fetch_data()
    result = await process_data(data)
    return result

# ❌ Bad
async def process():
    data = fetch_data()  # Forgot await
    result = await process_data(data)
    return result
```

### 4. Use asyncio.gather for Concurrent Operations

```python
# ✅ Good - runs concurrently
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3)
)

# ❌ Bad - runs sequentially
results = []
results.append(await fetch_user(1))
results.append(await fetch_user(2))
results.append(await fetch_user(3))
```

## Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected
```

## Debugging Async Code

### 1. Enable Async Debug Mode

```python
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # Windows
loop = asyncio.get_event_loop()
loop.set_debug(True)
```

### 2. Check for Blocking Operations

```python
import warnings
warnings.simplefilter('always', ResourceWarning)
```

### 3. Profile Async Performance

```python
import cProfile
import asyncio

async def main():
    await your_async_function()

cProfile.run('asyncio.run(main())')
```

## Common Pitfalls

### 1. Forgetting await

```python
# ❌ Wrong
result = async_function()  # Returns coroutine

# ✅ Correct
result = await async_function()
```

### 2. Blocking the Event Loop

```python
# ❌ Wrong - blocks event loop
import time
time.sleep(5)

# ✅ Correct - non-blocking
await asyncio.sleep(5)
```

### 3. Not Using Executor for CPU Work

```python
# ❌ Wrong - blocks event loop
def parse_large_file():
    # CPU-intensive work
    pass

result = parse_large_file()

# ✅ Correct - runs in thread pool
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, parse_large_file)
```

## Migration from Sync to Async

If you have sync code that needs to be async:

### 1. Add async/await

```python
# Before
def my_function():
    return result

# After
async def my_function():
    return result
```

### 2. Update Callers

```python
# Before
result = my_function()

# After
result = await my_function()
```

### 3. Use Async Libraries

```python
# Before
import requests
response = requests.get(url)

# After
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

## Performance Tips

1. **Use connection pooling** for API clients
2. **Batch operations** when possible
3. **Use asyncio.gather** for concurrent operations
4. **Profile** to find bottlenecks
5. **Monitor** event loop lag

## Monitoring Async Performance

```python
import asyncio
import time

async def monitor_event_loop():
    while True:
        start = time.time()
        await asyncio.sleep(0.1)
        lag = time.time() - start - 0.1
        if lag > 0.01:
            logger.warning(f"Event loop lag: {lag:.3f}s")
```

## Summary

Archie's async architecture provides:
- ✅ Better performance under load
- ✅ Concurrent request handling
- ✅ Non-blocking I/O
- ✅ Efficient resource usage
- ✅ Scalable design

All while maintaining clean, readable code with proper async/await patterns.

---

**For questions or issues with async code, see TROUBLESHOOTING.md**
