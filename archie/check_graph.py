#!/usr/bin/env python3
"""Check what's in the loaded graph."""
import pickle

# Load the graph
with open('.graph.pkl', 'rb') as f:
    graph = pickle.load(f)

print(f"Total nodes: {len(graph.nodes)}")
print(f"Total edges: {len(graph.edges)}")

# Count by type
node_types = {}
for node_id in graph.nodes:
    node_type = graph.nodes[node_id].get('type', 'unknown')
    node_types[node_type] = node_types.get(node_type, 0) + 1

print("\nNodes by type:")
for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {node_type}: {count}")

# Show some sample nodes
print("\nSample file nodes:")
file_nodes = [n for n in graph.nodes if graph.nodes[n].get('type') == 'file'][:5]
for node_id in file_nodes:
    print(f"  {node_id}")

print("\nSample function nodes:")
func_nodes = [n for n in graph.nodes if graph.nodes[n].get('type') == 'function'][:5]
for node_id in func_nodes:
    node = graph.nodes[node_id]
    print(f"  {node.get('name', node_id)} in {node.get('file_path', 'unknown')}")

print("\nSample class nodes:")
class_nodes = [n for n in graph.nodes if graph.nodes[n].get('type') == 'class'][:5]
for node_id in class_nodes:
    node = graph.nodes[node_id]
    print(f"  {node.get('name', node_id)} in {node.get('file_path', 'unknown')}")
