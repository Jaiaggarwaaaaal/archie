"""Knowledge graph using NetworkX."""
import networkx as nx
from typing import Dict, List, Optional, Any
import pickle


class CodeGraph:
    """Manages the codebase knowledge graph."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self._node_counter = 0
    
    def add_file(self, parsed_file: Dict) -> None:
        """Add a parsed file to the graph."""
        file_path = parsed_file["file_path"]
        
        # Add file node
        file_node_id = f"file:{file_path}"
        self.graph.add_node(
            file_node_id,
            type="file",
            file_path=file_path,
            name=file_path,
            language=parsed_file["language"]
        )
        
        # Add function nodes
        for func in parsed_file["functions"]:
            func_id = f"func:{file_path}:{func['name']}"
            self.graph.add_node(
                func_id,
                type="function",
                file_path=file_path,
                name=func["name"],
                line_start=func["line_start"],
                line_end=func["line_end"],
                params=func["params"]
            )
            # File contains function
            self.graph.add_edge(file_node_id, func_id, type="contains")
        
        # Add class nodes
        for cls in parsed_file["classes"]:
            cls_id = f"class:{file_path}:{cls['name']}"
            self.graph.add_node(
                cls_id,
                type="class",
                file_path=file_path,
                name=cls["name"]
            )
            # File contains class
            self.graph.add_edge(file_node_id, cls_id, type="contains")
            
            # Class contains methods
            for method in cls["methods"]:
                method_id = f"func:{file_path}:{cls['name']}.{method}"
                if self.graph.has_node(method_id):
                    self.graph.add_edge(cls_id, method_id, type="contains")
        
        # Add import edges
        for imp in parsed_file["imports"]:
            module = imp["module"]
            # Create import edge from file to module
            self.graph.add_edge(file_node_id, f"module:{module}", type="imports")
        
        # Add call edges
        for call in parsed_file["calls"]:
            caller_id = f"func:{file_path}:{call['caller']}"
            callee_name = call["callee"]
            
            # Try to find the callee in the graph
            callee_nodes = [n for n in self.graph.nodes() 
                          if self.graph.nodes[n].get("name") == callee_name 
                          and self.graph.nodes[n].get("type") == "function"]
            
            if callee_nodes:
                for callee_id in callee_nodes:
                    self.graph.add_edge(caller_id, callee_id, type="calls", line=call["line"])
            else:
                # Create placeholder for external function
                callee_id = f"func:external:{callee_name}"
                if not self.graph.has_node(callee_id):
                    self.graph.add_node(callee_id, type="function", name=callee_name, external=True)
                self.graph.add_edge(caller_id, callee_id, type="calls", line=call["line"])
    
    def get_node(self, name: str) -> Optional[Dict]:
        """Get node by name."""
        for node_id in self.graph.nodes():
            if self.graph.nodes[node_id].get("name") == name:
                return dict(self.graph.nodes[node_id], id=node_id)
        return None

    def get_callers(self, function_name: str) -> List[Dict]:
        """Get all functions that call this function."""
        callers = []
        target_nodes = [n for n in self.graph.nodes() 
                       if self.graph.nodes[n].get("name") == function_name]
        
        for target in target_nodes:
            for predecessor in self.graph.predecessors(target):
                edge_data = self.graph.get_edge_data(predecessor, target)
                if edge_data and edge_data.get("type") == "calls":
                    callers.append(dict(self.graph.nodes[predecessor], id=predecessor))
        return callers
    
    def get_callees(self, function_name: str) -> List[Dict]:
        """Get all functions that this function calls."""
        callees = []
        source_nodes = [n for n in self.graph.nodes() 
                       if self.graph.nodes[n].get("name") == function_name]
        
        for source in source_nodes:
            for successor in self.graph.successors(source):
                edge_data = self.graph.get_edge_data(source, successor)
                if edge_data and edge_data.get("type") == "calls":
                    callees.append(dict(self.graph.nodes[successor], id=successor))
        return callees
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get full dependency chain for a file."""
        file_node_id = f"file:{file_path}"
        if not self.graph.has_node(file_node_id):
            return []
        
        dependencies = []
        for successor in self.graph.successors(file_node_id):
            edge_data = self.graph.get_edge_data(file_node_id, successor)
            if edge_data and edge_data.get("type") == "imports":
                dependencies.append(successor)
        return dependencies

    def find_similar_nodes(self, name: str) -> List[Dict]:
        """Find nodes with similar names."""
        similar = []
        name_lower = name.lower()
        for node_id in self.graph.nodes():
            node_name = self.graph.nodes[node_id].get("name", "")
            if name_lower in node_name.lower() or node_name.lower() in name_lower:
                similar.append(dict(self.graph.nodes[node_id], id=node_id))
        return similar
    
    def subgraph_around(self, node_id: str, depth: int = 2) -> Dict:
        """Get subgraph around a node for context."""
        if not self.graph.has_node(node_id):
            return {"nodes": [], "edges": []}
        
        # BFS to get nodes within depth
        visited = {node_id}
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Add predecessors and successors
                next_level.update(self.graph.predecessors(node))
                next_level.update(self.graph.successors(node))
            visited.update(next_level)
            current_level = next_level
        
        # Build subgraph data
        nodes = []
        edges = []
        
        for node in visited:
            nodes.append(dict(self.graph.nodes[node], id=node))
        
        for node in visited:
            for successor in self.graph.successors(node):
                if successor in visited:
                    edge_data = self.graph.get_edge_data(node, successor)
                    edges.append({
                        "source": node,
                        "target": successor,
                        **edge_data
                    })
        
        return {"nodes": nodes, "edges": edges}

    def remove_file_nodes(self, file_path: str) -> None:
        """Remove all nodes associated with a file."""
        nodes_to_remove = [
            n for n in self.graph.nodes()
            if self.graph.nodes[n].get("file_path") == file_path
        ]
        self.graph.remove_nodes_from(nodes_to_remove)
    
    def save(self, path: str) -> None:
        """Persist graph to disk."""
        with open(path, "wb") as f:
            pickle.dump(self.graph, f)
    
    def load(self, path: str) -> None:
        """Load graph from disk."""
        with open(path, "rb") as f:
            self.graph = pickle.load(f)
    
    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "files": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "file"]),
            "functions": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "function"]),
            "classes": len([n for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "class"])
        }
        return stats
