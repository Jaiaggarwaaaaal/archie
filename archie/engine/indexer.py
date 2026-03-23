"""Orchestrates parser, graph, and embeddings for full repo indexing."""
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime
import asyncio
import hashlib
import aiofiles

from archie.engine.parser import CodeParser
from archie.engine.graph import CodeGraph
from archie.engine.embeddings import EmbeddingsStore

logger = logging.getLogger(__name__)


class CodeIndexer:
    """Orchestrates indexing of a codebase."""
    
    def __init__(self, embeddings_path: str, graph_path: Optional[str] = None):
        self.parser = CodeParser()
        self.graph = CodeGraph()
        self.embeddings = EmbeddingsStore(embeddings_path)
        self.graph_path = graph_path
        self.last_indexed = None
        
        # Track file hashes to detect actual changes
        self.file_hashes: Dict[str, str] = {}
    
    async def _compute_file_hash(self, file_path: str) -> Optional[str]:
        """Compute SHA256 hash of file content (async I/O)."""
        try:
            import aiofiles
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash {file_path}: {e}")
            return None
    
    async def _has_file_changed(self, file_path: str) -> bool:
        """Check if file has actually changed since last index (async)."""
        current_hash = await self._compute_file_hash(file_path)
        if current_hash is None:
            return True  # Assume changed if we can't hash
        
        previous_hash = self.file_hashes.get(file_path)
        if previous_hash is None:
            return True  # New file
        
        return current_hash != previous_hash
    
    async def index_repo(self, repo_path: str) -> None:
        """Full initial index of a repository."""
        logger.info(f"Starting full index of {repo_path}")
        repo = Path(repo_path)
        
        if not repo.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Find all Python and JS/TS files
        file_patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"]
        files_to_index = []
        
        for pattern in file_patterns:
            files_to_index.extend(repo.glob(pattern))
        
        # Filter out common directories to skip
        skip_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build"}
        files_to_index = [
            f for f in files_to_index 
            if not any(skip_dir in f.parts for skip_dir in skip_dirs)
        ]
        
        logger.info(f"Found {len(files_to_index)} files to index")
        
        # PARALLEL PROCESSING - Process 10 files at once
        batch_size = 10
        total_files = len(files_to_index)
        
        for i in range(0, total_files, batch_size):
            batch = files_to_index[i:i+batch_size]
            
            # Process batch in parallel
            tasks = []
            for file_path in batch:
                tasks.append(self.update_file(str(file_path), force=True))
            
            # Wait for all files in batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log errors
            for file_path, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.error(f"Error indexing {file_path}: {result}")
            
            # Progress logging
            progress = min(i + batch_size, total_files)
            percent = (progress * 100) // total_files
            logger.info(f"📊 Progress: {progress}/{total_files} files ({percent}%)")
        
        self.last_indexed = datetime.now()
        
        # Persist graph if path provided
        if self.graph_path:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.graph.save, self.graph_path)
        
        logger.info(f"Indexing complete. Stats: {self.graph.get_stats()}")

    async def update_file(self, file_path: str, force: bool = False) -> None:
        """Incremental update for a single file (fully async).
        
        Args:
            file_path: Path to file to update
            force: If True, update even if file hasn't changed
        """
        # Check if file changed (async I/O)
        if not force and not await self._has_file_changed(file_path):
            logger.debug(f"Skipping {file_path} - no changes detected")
            return
        
        logger.debug(f"Updating index for {file_path}")
        
        # Remove old nodes (fast, in-memory)
        self.graph.remove_file_nodes(file_path)
        self.embeddings.remove_by_file(file_path)
        
        # Parse file (CPU-bound, run in executor)
        loop = asyncio.get_event_loop()
        parsed = await loop.run_in_executor(None, self.parser.parse_file, file_path)
        
        if parsed is None:
            logger.warning(f"Could not parse {file_path}")
            return
        
        # Add to graph (fast, in-memory)
        self.graph.add_file(parsed)
        
        # Embed nodes (CPU-bound, run in executor)
        await self._embed_parsed_nodes(parsed, file_path)
        
        # Update hash cache (async I/O)
        new_hash = await self._compute_file_hash(file_path)
        if new_hash:
            self.file_hashes[file_path] = new_hash
        
        logger.debug(f"Updated {file_path}")
    
    async def _embed_parsed_nodes(self, parsed: Dict, file_path: str) -> None:
        """Embed all functions and classes (CPU-bound, run in executor)."""
        loop = asyncio.get_event_loop()
        
        # Embed functions
        for func in parsed["functions"]:
            node = {
                "id": f"func:{file_path}:{func['name']}",
                "file_path": file_path,
                "name": func["name"],
                "type": "function",
                "params": func.get("params", [])
            }
            # Run embedding in executor (CPU-bound)
            await loop.run_in_executor(None, self.embeddings.embed_node, node)
        
        # Embed classes
        for cls in parsed["classes"]:
            node = {
                "id": f"class:{file_path}:{cls['name']}",
                "file_path": file_path,
                "name": cls["name"],
                "type": "class"
            }
            # Run embedding in executor (CPU-bound)
            await loop.run_in_executor(None, self.embeddings.embed_node, node)
    
    def get_architecture_summary(self) -> Dict:
        """Get high-level architecture summary."""
        stats = self.graph.get_stats()
        embedding_stats = self.embeddings.get_stats()
        
        return {
            "last_indexed": self.last_indexed.isoformat() if self.last_indexed else None,
            "graph": stats,
            "embeddings": embedding_stats
        }
