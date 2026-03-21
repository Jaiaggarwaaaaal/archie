"""Graph visualization utilities."""
import json
from typing import Dict, List, Optional
from archie.engine.graph import CodeGraph


class GraphVisualizer:
    """Visualize the code knowledge graph."""
    
    def __init__(self, graph: CodeGraph):
        self.graph = graph
    
    def to_json(self, max_nodes: Optional[int] = None) -> Dict:
        """Export graph to JSON format for visualization.
        
        Args:
            max_nodes: Limit number of nodes (for large graphs)
        
        Returns:
            Dict with nodes and edges in format compatible with D3.js, Cytoscape, etc.
        """
        nodes = []
        edges = []
        
        # Get all nodes
        graph_nodes = list(self.graph.graph.nodes())
        if max_nodes:
            graph_nodes = graph_nodes[:max_nodes]
        
        for node_id in graph_nodes:
            node_data = self.graph.graph.nodes[node_id]
            nodes.append({
                "id": node_id,
                "label": node_data.get("name", node_id),
                "type": node_data.get("type", "unknown"),
                "file_path": node_data.get("file_path", ""),
                "line_start": node_data.get("line_start"),
                "line_end": node_data.get("line_end")
            })
        
        # Get all edges
        for source, target in self.graph.graph.edges():
            if source in graph_nodes and target in graph_nodes:
                edge_data = self.graph.graph.get_edge_data(source, target)
                edges.append({
                    "source": source,
                    "target": target,
                    "type": edge_data.get("type", "unknown"),
                    "line": edge_data.get("line")
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": self.graph.get_stats()
        }
    
    def to_mermaid(self, file_path: Optional[str] = None, depth: int = 2) -> str:
        """Generate Mermaid diagram for a file or entire graph.
        
        Args:
            file_path: Focus on specific file (None for entire graph)
            depth: How many levels to show
        
        Returns:
            Mermaid diagram syntax
        """
        lines = ["graph TD"]
        
        if file_path:
            # Show subgraph around file
            file_node_id = f"file:{file_path}"
            if self.graph.graph.has_node(file_node_id):
                subgraph = self.graph.subgraph_around(file_node_id, depth=depth)
                nodes = subgraph["nodes"]
                edges = subgraph["edges"]
            else:
                return "graph TD\n    A[File not found]"
        else:
            # Show entire graph (limited)
            nodes = [
                {"id": n, **self.graph.graph.nodes[n]} 
                for n in list(self.graph.graph.nodes())[:50]
            ]
            edges = [
                {
                    "source": s,
                    "target": t,
                    **self.graph.graph.get_edge_data(s, t)
                }
                for s, t in list(self.graph.graph.edges())[:100]
            ]
        
        # Add nodes
        for node in nodes:
            node_id = node["id"].replace(":", "_").replace("/", "_").replace(".", "_")
            node_name = node.get("name", node["id"])
            node_type = node.get("type", "unknown")
            
            # Style based on type
            if node_type == "file":
                lines.append(f'    {node_id}["{node_name}"]')
                lines.append(f'    style {node_id} fill:#e1f5ff')
            elif node_type == "function":
                lines.append(f'    {node_id}("{node_name}()")')
                lines.append(f'    style {node_id} fill:#fff4e6')
            elif node_type == "class":
                lines.append(f'    {node_id}["{node_name}"]')
                lines.append(f'    style {node_id} fill:#f3e5f5')
        
        # Add edges
        for edge in edges:
            source_id = edge["source"].replace(":", "_").replace("/", "_").replace(".", "_")
            target_id = edge["target"].replace(":", "_").replace("/", "_").replace(".", "_")
            edge_type = edge.get("type", "")
            
            # Different arrow styles for different edge types
            if edge_type == "calls":
                lines.append(f'    {source_id} -->|calls| {target_id}')
            elif edge_type == "imports":
                lines.append(f'    {source_id} -.->|imports| {target_id}')
            elif edge_type == "contains":
                lines.append(f'    {source_id} ==>|contains| {target_id}')
            else:
                lines.append(f'    {source_id} --> {target_id}')
        
        return "\n".join(lines)
    
    def get_file_dependencies(self, file_path: str) -> Dict:
        """Get all dependencies for a file.
        
        Returns:
            Dict with imports, imported_by, calls, called_by
        """
        file_node_id = f"file:{file_path}"
        if not self.graph.graph.has_node(file_node_id):
            return {"error": "File not found in graph"}
        
        # Get what this file imports
        imports = []
        for successor in self.graph.graph.successors(file_node_id):
            edge_data = self.graph.graph.get_edge_data(file_node_id, successor)
            if edge_data and edge_data.get("type") == "imports":
                imports.append(successor)
        
        # Get what imports this file
        imported_by = []
        for predecessor in self.graph.graph.predecessors(file_node_id):
            edge_data = self.graph.graph.get_edge_data(predecessor, file_node_id)
            if edge_data and edge_data.get("type") == "imports":
                imported_by.append(predecessor)
        
        # Get functions in this file
        functions = []
        for successor in self.graph.graph.successors(file_node_id):
            node_data = self.graph.graph.nodes[successor]
            if node_data.get("type") == "function":
                # Get what this function calls
                calls = [
                    self.graph.graph.nodes[s].get("name")
                    for s in self.graph.graph.successors(successor)
                ]
                # Get what calls this function
                called_by = [
                    self.graph.graph.nodes[p].get("name")
                    for p in self.graph.graph.predecessors(successor)
                ]
                
                functions.append({
                    "name": node_data.get("name"),
                    "calls": calls,
                    "called_by": called_by
                })
        
        return {
            "file": file_path,
            "imports": imports,
            "imported_by": imported_by,
            "functions": functions
        }
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the graph.
        
        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        import networkx as nx
        
        try:
            cycles = list(nx.simple_cycles(self.graph.graph))
            return cycles[:10]  # Limit to first 10
        except:
            return []
    
    def get_most_connected_nodes(self, top_n: int = 10) -> List[Dict]:
        """Get the most connected nodes (potential hotspots).
        
        Args:
            top_n: Number of top nodes to return
        
        Returns:
            List of nodes with their connection counts
        """
        node_degrees = []
        
        for node_id in self.graph.graph.nodes():
            in_degree = self.graph.graph.in_degree(node_id)
            out_degree = self.graph.graph.out_degree(node_id)
            total_degree = in_degree + out_degree
            
            node_data = self.graph.graph.nodes[node_id]
            node_degrees.append({
                "id": node_id,
                "name": node_data.get("name", node_id),
                "type": node_data.get("type", "unknown"),
                "in_degree": in_degree,
                "out_degree": out_degree,
                "total_degree": total_degree
            })
        
        # Sort by total degree
        node_degrees.sort(key=lambda x: x["total_degree"], reverse=True)
        
        return node_degrees[:top_n]
