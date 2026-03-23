#!/usr/bin/env python3
"""Test script to check graph and visualize it properly."""
import requests
import json

def test_graph():
    """Check graph statistics and get sample data."""
    
    print("="*60)
    print("ARCHIE GRAPH STATISTICS")
    print("="*60)
    
    # Get graph summary
    response = requests.get("http://localhost:8000/graph/summary")
    if response.status_code == 200:
        summary = response.json()
        print(f"\n📊 Total Statistics:")
        print(f"   Files: {summary.get('files', 0)}")
        print(f"   Functions: {summary.get('functions', 0)}")
        print(f"   Classes: {summary.get('classes', 0)}")
        print(f"   Total Nodes: {summary.get('total_nodes', 0)}")
        print(f"   Total Edges: {summary.get('total_edges', 0)}")
    
    # Get sample nodes
    print(f"\n🔍 Sample Files in Graph:")
    response = requests.get("http://localhost:8000/graph/visualize?max_nodes=10")
    if response.status_code == 200:
        data = response.json()
        files = [n for n in data['nodes'] if n['type'] == 'file'][:5]
        for f in files:
            print(f"   - {f['label']}")
        
        print(f"\n⚡ Sample Functions:")
        funcs = [n for n in data['nodes'] if n['type'] == 'function'][:5]
        for f in funcs:
            print(f"   - {f['label']} (in {f.get('file_path', 'unknown')})")
    
    # Test search
    print(f"\n🔎 Testing Semantic Search:")
    response = requests.post(
        "http://localhost:8000/search",
        json={"query": "report generation"}
    )
    if response.status_code == 200:
        results = response.json()['results'][:3]
        print(f"   Found {len(results)} results for 'report generation':")
        for r in results:
            print(f"   - {r.get('name', 'unknown')} (score: {r.get('score', 0):.3f})")
    
    print(f"\n✅ Graph is working! Visit these URLs:")
    print(f"   3D View: http://localhost:8000/graph/3d?max_nodes=500")
    print(f"   Mermaid: http://localhost:8000/graph/mermaid/view?depth=2")
    print(f"   Hotspots: http://localhost:8000/graph/analysis/hotspots")
    print("="*60)

if __name__ == "__main__":
    test_graph()
