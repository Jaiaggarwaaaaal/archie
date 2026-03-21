# Graph Visualization Guide

## Overview

Archie provides multiple ways to visualize your codebase's knowledge graph, helping you understand code relationships, dependencies, and architecture.

## 🌟 3D Interactive Graph (Recommended)

### Access
```bash
http://localhost:8000/graph/3d
```

### Features

**Interactive Controls:**
- 🖱️ **Drag** - Rotate the graph in 3D space
- 🔍 **Scroll** - Zoom in/out
- 👆 **Click node** - View detailed information
- 🎯 **Auto-rotate** - Smooth camera movement

**Visual Elements:**
- 🔵 **Blue nodes** - Files
- 🟠 **Orange nodes** - Functions
- 🟣 **Purple nodes** - Classes
- 🔴 **Red edges** - Function calls (animated)
- 🟢 **Green edges** - Contains relationships
- 🔷 **Cyan edges** - Import relationships

**Information Panel:**
- Node name and type
- File path
- Line numbers
- Connection count

### Parameters

```bash
# Limit number of nodes
http://localhost:8000/graph/3d?max_nodes=100

# Filter by file pattern
http://localhost:8000/graph/3d?file_filter=payment

# Combine filters
http://localhost:8000/graph/3d?max_nodes=50&file_filter=user
```

### Use Cases

**1. Understand Architecture**
```
View entire codebase structure
→ See how modules connect
→ Identify central components
```

**2. Find Dependencies**
```
Click on a file node
→ See what it imports (cyan edges)
→ See what imports it
→ Trace dependency chains
```

**3. Analyze Function Calls**
```
Click on a function node
→ See animated red edges (calls)
→ Understand call flow
→ Find call chains
```

**4. Identify Hotspots**
```
Look for nodes with many connections
→ These are critical components
→ Changes here affect many files
→ Need careful testing
```

## 📊 2D Mermaid Diagrams

### Access
```bash
http://localhost:8000/graph/mermaid/view
```

### Features

**Static Diagram:**
- Clear hierarchical layout
- Easy to screenshot/share
- Good for documentation

**Focus on Specific File:**
```bash
http://localhost:8000/graph/mermaid/view?file_path=src/payment.py&depth=2
```

**Depth Control:**
- `depth=1` - Direct connections only
- `depth=2` - Two levels of connections
- `depth=3` - Three levels (can get large)

### Use Cases

**1. Documentation**
```
Generate diagram for specific module
→ Add to README
→ Share with team
→ Include in design docs
```

**2. Code Reviews**
```
Show impact of changes
→ What depends on this file?
→ What does this file depend on?
→ Visualize before/after
```

**3. Onboarding**
```
Help new developers understand
→ Module structure
→ Key dependencies
→ Entry points
```

## 📈 JSON Export

### Access
```bash
http://localhost:8000/graph/visualize?max_nodes=200
```

### Response Format
```json
{
  "nodes": [
    {
      "id": "file:payment.py",
      "label": "payment.py",
      "type": "file",
      "file_path": "payment.py",
      "line_start": null,
      "line_end": null
    },
    {
      "id": "func:payment.py:process_payment",
      "label": "process_payment",
      "type": "function",
      "file_path": "payment.py",
      "line_start": 12,
      "line_end": 34
    }
  ],
  "edges": [
    {
      "source": "func:payment.py:process_payment",
      "target": "func:validators.py:validate_card",
      "type": "calls",
      "line": 18
    }
  ],
  "stats": {
    "total_nodes": 150,
    "total_edges": 200,
    "files": 10,
    "functions": 120,
    "classes": 20
  }
}
```

### Use Cases

**1. Custom Visualizations**
```javascript
// Use with D3.js
fetch('/graph/visualize')
  .then(r => r.json())
  .then(data => {
    // Create custom D3 visualization
    d3.forceSimulation(data.nodes)...
  });
```

**2. Analysis Scripts**
```python
import requests
import networkx as nx

# Get graph data
data = requests.get('http://localhost:8000/graph/visualize').json()

# Analyze with NetworkX
G = nx.DiGraph()
for node in data['nodes']:
    G.add_node(node['id'], **node)
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], **edge)

# Find shortest path
path = nx.shortest_path(G, source, target)
```

**3. Export to Other Tools**
```bash
# Export to Gephi, Cytoscape, etc.
curl http://localhost:8000/graph/visualize > graph.json
```

## 🔍 Dependency Analysis

### File Dependencies
```bash
http://localhost:8000/graph/file/src/payment.py/dependencies
```

**Response:**
```json
{
  "file": "src/payment.py",
  "imports": ["module:validators", "module:database"],
  "imported_by": ["file:api.py", "file:cli.py"],
  "functions": [
    {
      "name": "process_payment",
      "calls": ["validate_card", "save_transaction"],
      "called_by": ["handle_checkout", "retry_payment"]
    }
  ]
}
```

### Use Cases

**1. Impact Analysis**
```
Before changing a file:
→ Check what imports it
→ Check what it calls
→ Estimate blast radius
```

**2. Refactoring**
```
Moving a function?
→ See all callers
→ Update imports
→ Verify nothing breaks
```

**3. Dead Code Detection**
```
Function with no callers?
→ Might be dead code
→ Safe to remove
→ Clean up codebase
```

## 🔄 Circular Dependencies

### Access
```bash
http://localhost:8000/graph/analysis/circular
```

**Response:**
```json
{
  "cycles_found": 2,
  "cycles": [
    ["file:a.py", "file:b.py", "file:a.py"],
    ["func:x", "func:y", "func:z", "func:x"]
  ]
}
```

### Use Cases

**1. Find Problems**
```
Circular dependencies are bad
→ Hard to test
→ Hard to understand
→ Can cause import errors
```

**2. Refactoring Targets**
```
Break circular dependencies
→ Extract common code
→ Use dependency injection
→ Improve architecture
```

## 🔥 Hotspot Analysis

### Access
```bash
http://localhost:8000/graph/analysis/hotspots?top_n=10
```

**Response:**
```json
{
  "hotspots": [
    {
      "id": "func:utils.py:validate",
      "name": "validate",
      "type": "function",
      "in_degree": 45,
      "out_degree": 3,
      "total_degree": 48
    }
  ],
  "message": "These are the most connected nodes in your codebase"
}
```

### Use Cases

**1. Identify Critical Code**
```
High degree = many connections
→ Central to architecture
→ Changes affect many files
→ Need thorough testing
```

**2. Refactoring Priorities**
```
Hotspots are good candidates for:
→ Breaking into smaller functions
→ Adding comprehensive tests
→ Improving documentation
```

**3. Risk Assessment**
```
Before deploying:
→ Check if hotspots changed
→ Extra testing needed
→ Higher risk of bugs
```

## 🎨 Visualization Best Practices

### 1. Start with 3D Graph
```
First time exploring codebase?
→ Use 3D graph
→ Get overall sense
→ Identify interesting areas
```

### 2. Drill Down with Filters
```
Found interesting area?
→ Filter by file pattern
→ Reduce node count
→ Focus on specific module
```

### 3. Use Mermaid for Documentation
```
Need to explain something?
→ Generate Mermaid diagram
→ Add to docs
→ Share with team
```

### 4. Export for Analysis
```
Need detailed analysis?
→ Export to JSON
→ Use Python/NetworkX
→ Custom metrics
```

### 5. Regular Checks
```
Weekly/monthly:
→ Check for circular dependencies
→ Review hotspots
→ Monitor complexity growth
```

## 🚀 Advanced Usage

### Custom Visualization

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <svg id="graph"></svg>
    <script>
        // Fetch graph data
        fetch('http://localhost:8000/graph/visualize')
            .then(r => r.json())
            .then(data => {
                // Create custom D3 visualization
                const svg = d3.select('#graph');
                const simulation = d3.forceSimulation(data.nodes)
                    .force('link', d3.forceLink(data.edges).id(d => d.id))
                    .force('charge', d3.forceManyBody())
                    .force('center', d3.forceCenter(400, 300));
                
                // Add links
                const link = svg.append('g')
                    .selectAll('line')
                    .data(data.edges)
                    .enter().append('line');
                
                // Add nodes
                const node = svg.append('g')
                    .selectAll('circle')
                    .data(data.nodes)
                    .enter().append('circle')
                    .attr('r', 5);
                
                // Update positions
                simulation.on('tick', () => {
                    link
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);
                    
                    node
                        .attr('cx', d => d.x)
                        .attr('cy', d => d.y);
                });
            });
    </script>
</body>
</html>
```

### Python Analysis

```python
import requests
import networkx as nx
import matplotlib.pyplot as plt

# Get graph data
response = requests.get('http://localhost:8000/graph/visualize')
data = response.json()

# Build NetworkX graph
G = nx.DiGraph()
for node in data['nodes']:
    G.add_node(node['id'], **node)
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], **edge)

# Analyze
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
print(f"Density: {nx.density(G):.3f}")

# Find most central nodes
centrality = nx.betweenness_centrality(G)
top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nMost central nodes:")
for node, score in top_central:
    print(f"  {node}: {score:.3f}")

# Visualize
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=500, font_size=8, arrows=True)
plt.savefig('graph.png')
```

## 📝 Tips & Tricks

### Performance
- Limit nodes for large codebases (`max_nodes=100`)
- Use filters to focus on specific areas
- 3D graph works best with <500 nodes

### Understanding
- Blue = structure (files)
- Orange = behavior (functions)
- Purple = organization (classes)
- Red edges = runtime flow (calls)

### Exploration
- Start zoomed out (big picture)
- Click interesting nodes (details)
- Follow edges (relationships)
- Look for clusters (modules)

### Documentation
- Screenshot 3D graph for presentations
- Export Mermaid for markdown docs
- Use JSON for automated reports

---

**The 3D graph is the best way to explore and understand your codebase visually!** 🚀
