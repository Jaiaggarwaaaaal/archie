#!/usr/bin/env python3
"""
Quick script to verify Archie graph is working correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def check_graph():
    print("=" * 70)
    print("🔍 ARCHIE GRAPH VERIFICATION")
    print("=" * 70)
    
    # 1. Check summary
    print("\n1️⃣  Checking graph summary...")
    resp = requests.get(f"{BASE_URL}/graph/summary")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Graph indexed: {data['last_indexed']}")
        print(f"   📊 Total nodes: {data['graph']['total_nodes']:,}")
        print(f"   🔗 Total edges: {data['graph']['total_edges']:,}")
        print(f"   📁 Files: {data['graph']['files']:,}")
        print(f"   🔧 Functions: {data['graph']['functions']:,}")
        print(f"   📦 Classes: {data['graph']['classes']:,}")
        print(f"   🧠 Embeddings: {data['embeddings']['total_embeddings']:,}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
        return
    
    # 2. Check visualization data
    print("\n2️⃣  Checking visualization data...")
    resp = requests.get(f"{BASE_URL}/graph/visualize?max_nodes=100")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Nodes: {len(data['nodes'])}")
        print(f"   ✅ Edges: {len(data['edges'])}")
        
        # Show node types
        types = {}
        for n in data['nodes']:
            t = n['type']
            types[t] = types.get(t, 0) + 1
        print(f"   📊 Node types:")
        for t, count in sorted(types.items()):
            print(f"      - {t}: {count}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
        return
    
    # 3. Check UI endpoints
    print("\n3️⃣  Checking UI endpoints...")
    
    ui_endpoints = [
        ("/graph/ui", "2D Graph UI"),
        ("/graph/3d", "3D Graph Visualization"),
    ]
    
    for endpoint, name in ui_endpoints:
        resp = requests.get(f"{BASE_URL}{endpoint}")
        if resp.status_code == 200 and "html" in resp.text.lower():
            print(f"   ✅ {name}: {BASE_URL}{endpoint}")
        else:
            print(f"   ❌ {name}: Failed ({resp.status_code})")
    
    print("\n" + "=" * 70)
    print("✅ GRAPH IS READY!")
    print("=" * 70)
    print("\n📍 Open these URLs in your browser:")
    print(f"   • 2D Graph: {BASE_URL}/graph/ui")
    print(f"   • 3D Graph: {BASE_URL}/graph/3d")
    print(f"   • Summary: {BASE_URL}/graph/summary")
    print()

if __name__ == "__main__":
    try:
        check_graph()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Archie server")
        print("   Make sure Archie is running: python3 -m archie.main")
    except Exception as e:
        print(f"❌ Error: {e}")
