#!/usr/bin/env python3
"""Test script to send incident to Archie webhook."""
import requests
import json
import sys

def test_incident():
    """Send the example incident to Archie."""
    
    # Read the incident JSON
    with open('example_incident.json', 'r') as f:
        incident_data = json.load(f)
    
    print("Sending incident INC-207 to Archie...")
    print(f"Incident title: {incident_data['title']}")
    print(f"JSON size: {len(json.dumps(incident_data))} bytes")
    
    # Send to webhook
    url = "http://localhost:8000/webhook/incident"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=incident_data, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Incident processed successfully!")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to Archie. Is it running on http://localhost:8000?")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_incident()
