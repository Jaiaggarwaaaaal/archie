#!/bin/bash
# Test Archie with your codebase

echo "🤖 Testing Archie with Your Codebase"
echo "===================================="
echo ""

# Check if Archie is running
echo "1. Checking if Archie is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Archie is running"
else
    echo "   ❌ Archie is not running. Start it with: python -m archie.main"
    exit 1
fi

echo ""
echo "2. Triggering codebase indexing..."
curl -X POST http://localhost:8000/index/trigger
echo ""

echo ""
echo "3. Waiting for indexing to complete (30 seconds)..."
sleep 30

echo ""
echo "4. Checking index status..."
curl -s http://localhost:8000/index/status | python -m json.tool

echo ""
echo "5. Testing semantic search..."
curl -s -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "error handling"}' | python -m json.tool

echo ""
echo "6. Finding hotspots (most connected code)..."
curl -s http://localhost:8000/graph/analysis/hotspots | python -m json.tool

echo ""
echo "7. Finding circular dependencies..."
curl -s http://localhost:8000/graph/analysis/circular | python -m json.tool

echo ""
echo "8. Opening 3D graph visualization..."
echo "   Open in browser: http://localhost:8000/graph/3d"

echo ""
echo "9. Testing incident response..."
echo "   Sending your incident..."
curl -s -X POST http://localhost:8000/webhook/incident \
  -H "Content-Type: application/json" \
  -d @example_incident.json | python -m json.tool

echo ""
echo "===================================="
echo "✅ Test Complete!"
echo ""
echo "Next steps:"
echo "1. View 3D graph: http://localhost:8000/graph/3d"
echo "2. Check GitHub for PR (if incident was sent)"
echo "3. Review Archie's analysis"
echo ""
