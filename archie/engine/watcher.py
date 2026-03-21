"""File system watcher for incremental graph updates."""
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CodeFileHandler(FileSystemEventHandler):
    """Handles file system events for code files."""
    
    def __init__(self, indexer, extensions=None):
        self.indexer = indexer
        self.extensions = extensions or {".py", ".js", ".ts", ".jsx", ".tsx"}
    
    def _should_process(self, file_path: str) -> bool:
        """Check if file should be processed."""
        path = Path(file_path)
        
        # Check extension
        if path.suffix not in self.extensions:
            return False
        
        # Skip common directories
        skip_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build"}
        if any(skip_dir in path.parts for skip_dir in skip_dirs):
            return False
        
        return True
    
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
        
        if self._should_process(event.src_path):
            logger.info(f"File modified: {event.src_path}")
            try:
                self.indexer.update_file(event.src_path)
            except Exception as e:
                logger.error(f"Error updating {event.src_path}: {e}")
    
    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return
        
        if self._should_process(event.src_path):
            logger.info(f"File created: {event.src_path}")
            try:
                self.indexer.update_file(event.src_path)
            except Exception as e:
                logger.error(f"Error indexing {event.src_path}: {e}")


class CodeWatcher:
    """Watches a directory for code changes."""
    
    def __init__(self, indexer, repo_path: str):
        self.indexer = indexer
        self.repo_path = repo_path
        self.observer = Observer()
        self.handler = CodeFileHandler(indexer)
    
    def start(self):
        """Start watching the repository."""
        logger.info(f"Starting watcher for {self.repo_path}")
        self.observer.schedule(self.handler, self.repo_path, recursive=True)
        self.observer.start()
    
    def stop(self):
        """Stop watching."""
        logger.info("Stopping watcher")
        self.observer.stop()
        self.observer.join()
