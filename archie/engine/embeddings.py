"""Vector embeddings using LanceDB and sentence-transformers."""
import lancedb
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional
from pathlib import Path


class EmbeddingsStore:
    """Manages vector embeddings for code nodes."""
    
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.model = SentenceTransformer(model_name)
        self.db = lancedb.connect(db_path)
        self._init_table()
    
    def _init_table(self):
        """Initialize or connect to the embeddings table."""
        try:
            self.table = self.db.open_table("code_embeddings")
        except Exception:
            # Table doesn't exist, will be created on first insert
            self.table = None
    
    def embed_node(self, node: Dict) -> None:
        """Embed a code node and store it."""
        # Build text representation
        text_parts = [node.get("name", "")]
        
        # Add docstring if available
        if "docstring" in node:
            text_parts.append(node["docstring"])
        
        # Add parameters if available
        if "params" in node and node["params"]:
            text_parts.append(" ".join(node["params"]))
        
        text = " ".join(text_parts)
        
        # Generate embedding
        embedding = self.model.encode(text).tolist()
        
        # Prepare record
        record = {
            "node_id": node.get("id", ""),
            "file_path": node.get("file_path", ""),
            "name": node.get("name", ""),
            "type": node.get("type", ""),
            "vector": embedding,
            "text": text
        }
        
        # Store in LanceDB
        if self.table is None:
            self.table = self.db.create_table("code_embeddings", [record])
        else:
            self.table.add([record])
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search for similar code nodes."""
        if self.table is None:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()
        
        # Search
        results = self.table.search(query_embedding).limit(top_k).to_list()
        
        return [
            {
                "node_id": r["node_id"],
                "file_path": r["file_path"],
                "name": r["name"],
                "type": r["type"],
                "text": r["text"],
                "score": r.get("_distance", 0)
            }
            for r in results
        ]
    
    def find_duplicate(self, description: str) -> List[Dict]:
        """Find potentially duplicate code based on description."""
        return self.search(description, top_k=10)
    
    def remove_by_file(self, file_path: str) -> None:
        """Remove all embeddings for a specific file."""
        if self.table is None:
            return
        
        # LanceDB delete by filter
        try:
            self.table.delete(f"file_path = '{file_path}'")
        except Exception:
            pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get embedding store statistics."""
        if self.table is None:
            return {"total_embeddings": 0}
        
        count = self.table.count_rows()
        return {"total_embeddings": count}
