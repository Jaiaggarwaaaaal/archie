# Async I/O Patterns in Archie

## The Problem You Identified

You correctly spotted that `_update_file_sync` was mixing I/O-bound and CPU-bound operations incorrectly!

### Before (Incorrect)

```python
def _update_file_sync(self, file_path: str, force: bool = False):
    # ❌ Blocking I/O in sync function
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # ❌ CPU-bound work not in executor
    parsed = self.parser.parse_file(file_path)
    
    # ❌ More CPU-bound work
    self.embeddings.embed_node(node)
```

**Problems:**
1. File I/O blocks the event loop
2. CPU-bound work blocks the event loop
3. Can't handle concurrent file updates efficiently

### After (Correct)

```python
async def update_file(self, file_path: str, force: bool = False):
    # ✅ Async I/O (non-blocking)
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    
    # ✅ CPU-bound work in executor
    loop = asyncio.get_event_loop()
    parsed = await loop.run_in_executor(None, self.parser.parse_file, file_path)
    
    # ✅ More CPU-bound work in executor
    await loop.run_in_executor(None, self.embeddings.embed_node, node)
```

**Benefits:**
1. File I/O doesn't block event loop
2. CPU work runs in thread pool
3. Can process multiple files concurrently

## Operation Classification

### I/O-Bound (Use Async)

```python
# File operations
async with aiofiles.open('file.txt', 'r') as f:
    content = await f.read()

# Network operations
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# Database operations
result = await db.query(sql)
```

### CPU-Bound (Use Executor)

```python
loop = asyncio.get_event_loop()

# Parsing
parsed = await loop.run_in_executor(None, parser.parse_file, path)

# Embeddings
embedding = await loop.run_in_executor(None, model.encode, text)

# Hashing (if large files)
hash_val = await loop.run_in_executor(None, compute_hash, data)
```

### In-Memory (Direct Call)

```python
# Fast operations, no async needed
self.graph.add_node(node)
self.cache[key] = value
result = data.get(key)
```

## Complete Async Flow

### File Update Flow

```python
async def update_file(self, file_path: str):
    # 1. Check if changed (async I/O)
    if not await self._has_file_changed(file_path):
        return
    
    # 2. Remove old data (in-memory, fast)
    self.graph.remove_file_nodes(file_path)
    
    # 3. Parse file (CPU-bound, executor)
    loop = asyncio.get_event_loop()
    parsed = await loop.run_in_executor(None, self.parser.parse_file, file_path)
    
    # 4. Add to graph (in-memory, fast)
    self.graph.add_file(parsed)
    
    # 5. Generate embeddings (CPU-bound, executor)
    for func in parsed["functions"]:
        await loop.run_in_executor(None, self.embeddings.embed_node, func)
    
    # 6. Update hash (async I/O)
    new_hash = await self._compute_file_hash(file_path)
    self.file_hashes[file_path] = new_hash
```

### Concurrent Processing

```python
async def index_repo(self, repo_path: str):
    files = find_all_files(repo_path)
    
    # Process files concurrently (up to 10 at a time)
    semaphore = asyncio.Semaphore(10)
    
    async def process_with_limit(file_path):
        async with semaphore:
            await self.update_file(file_path)
    
    # Process all files concurrently
    await asyncio.gather(*[process_with_limit(f) for f in files])
```

## Performance Comparison

### Sequential (Blocking)

```python
# Before: Blocking I/O
for file in files:
    content = open(file).read()      # Blocks
    parsed = parse(content)          # Blocks
    embed = generate_embedding(parsed)  # Blocks

# 100 files × 100ms = 10 seconds
```

### Async (Non-Blocking)

```python
# After: Async I/O + Executor
async def process_file(file):
    content = await aiofiles.open(file).read()  # Non-blocking
    parsed = await executor(parse, content)      # Non-blocking
    embed = await executor(generate_embedding, parsed)  # Non-blocking

await asyncio.gather(*[process_file(f) for f in files])

# 100 files processed concurrently = ~2 seconds
```

## Best Practices

### 1. Use aiofiles for File I/O

```python
# ✅ Good - async file I/O
import aiofiles
async with aiofiles.open('file.txt', 'r') as f:
    content = await f.read()

# ❌ Bad - blocking file I/O
with open('file.txt', 'r') as f:
    content = f.read()
```

### 2. Use Executor for CPU Work

```python
# ✅ Good - CPU work in executor
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, cpu_intensive_function, arg)

# ❌ Bad - CPU work blocks event loop
result = cpu_intensive_function(arg)
```

### 3. Batch Executor Calls

```python
# ✅ Good - batch processing
loop = asyncio.get_event_loop()
tasks = [loop.run_in_executor(None, process, item) for item in items]
results = await asyncio.gather(*tasks)

# ❌ Bad - sequential processing
results = []
for item in items:
    result = await loop.run_in_executor(None, process, item)
    results.append(result)
```

### 4. Limit Concurrency

```python
# ✅ Good - controlled concurrency
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

async def process_with_limit(item):
    async with semaphore:
        return await process(item)

results = await asyncio.gather(*[process_with_limit(i) for i in items])

# ❌ Bad - unlimited concurrency (can overwhelm system)
results = await asyncio.gather(*[process(i) for i in items])
```

## Common Patterns

### Pattern 1: Read File → Process → Write Result

```python
async def process_file(input_path: str, output_path: str):
    # Read (async I/O)
    async with aiofiles.open(input_path, 'r') as f:
        content = await f.read()
    
    # Process (CPU-bound, executor)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, heavy_processing, content)
    
    # Write (async I/O)
    async with aiofiles.open(output_path, 'w') as f:
        await f.write(result)
```

### Pattern 2: Fetch → Parse → Store

```python
async def fetch_and_store(url: str):
    # Fetch (async I/O)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    # Parse (CPU-bound, executor)
    loop = asyncio.get_event_loop()
    parsed = await loop.run_in_executor(None, parse_data, response.text)
    
    # Store (in-memory, fast)
    self.cache[url] = parsed
```

### Pattern 3: Batch Processing

```python
async def process_batch(items: List[str]):
    # Process all items concurrently
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results
    for item, result in zip(items, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to process {item}: {result}")
        else:
            logger.info(f"Processed {item}: {result}")
```

## Debugging Async I/O

### 1. Check for Blocking Calls

```python
import asyncio

# Enable debug mode
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
loop = asyncio.get_event_loop()
loop.set_debug(True)
loop.slow_callback_duration = 0.1  # Warn if callback takes >100ms
```

### 2. Profile Async Operations

```python
import time

async def timed_operation(name: str, coro):
    start = time.time()
    result = await coro
    duration = time.time() - start
    logger.info(f"{name} took {duration:.3f}s")
    return result

# Use it
result = await timed_operation("parse_file", parse_file(path))
```

### 3. Monitor Event Loop Lag

```python
async def monitor_loop():
    while True:
        start = time.time()
        await asyncio.sleep(0.1)
        lag = time.time() - start - 0.1
        if lag > 0.01:
            logger.warning(f"Event loop lag: {lag*1000:.1f}ms")
```

## Performance Tips

### 1. Use Connection Pooling

```python
# ✅ Good - reuse client
class Indexer:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
    
    async def fetch(self, url):
        return await self.http_client.get(url)

# ❌ Bad - create new client each time
async def fetch(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

### 2. Batch Small Operations

```python
# ✅ Good - batch small files
async def process_small_files(files):
    # Read all at once
    contents = await asyncio.gather(*[read_file(f) for f in files])
    
    # Process in one executor call
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, batch_process, contents)

# ❌ Bad - individual processing
for file in files:
    content = await read_file(file)
    result = await loop.run_in_executor(None, process, content)
```

### 3. Use Appropriate Concurrency Limits

```python
# File I/O: Limit based on disk speed
file_semaphore = asyncio.Semaphore(50)  # 50 concurrent file ops

# CPU work: Limit to CPU count
import os
cpu_semaphore = asyncio.Semaphore(os.cpu_count())

# Network: Higher limit
network_semaphore = asyncio.Semaphore(100)
```

## Summary

Your observation was spot-on! The refactored code now:

✅ **Uses async I/O** for file operations (aiofiles)
✅ **Uses executor** for CPU-bound work (parsing, embeddings)
✅ **Doesn't block** the event loop
✅ **Processes files concurrently** when possible
✅ **Properly separates** I/O, CPU, and in-memory operations

This makes Archie significantly faster and more scalable!

---

**Key Takeaway:** Always classify operations as I/O-bound, CPU-bound, or in-memory, then use the appropriate async pattern for each.
