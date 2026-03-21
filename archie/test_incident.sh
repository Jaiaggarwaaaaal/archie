#!/bin/bash
# Test script to send incident to Archie webhook

echo "Sending incident INC-207 to Archie..."
curl -X POST http://localhost:8000/webhook/incident \
  -H "Content-Type: application/json" \
  --data-binary @example_incident.json

echo ""
echo "Done!"
