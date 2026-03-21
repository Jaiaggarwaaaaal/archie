#!/usr/bin/env python3
"""Test with a real file from the repo."""
import requests
import json
import sys

def test_real_incident():
    """Send incident with real file."""
    
    incident_data = {
        "source": "manual",
        "title": "TEST: Report generation issue",
        "error_message": "HTML report generation fails to include all test steps",
        "severity": "minor",
        "timestamp": "2026-03-20T10:00:00Z",
        "environment": "production",
        "affected_service": "Reporting",
        "details": {
            "affected_files": [
                "reporting/html_report.py"
            ],
            "stack_trace": "Report missing test steps in HTML output"
        }
    }
    
    print("Sending REAL incident to Archie...")
    print(f"Incident title: {incident_data['title']}")
    print(f"Affected file: reporting/html_report.py")
    
    url = "http://localhost:8000/webhook/incident"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=incident_data, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("INCIDENT INVESTIGATION RESULTS")
            print("="*60)
            
            print(f"\n✅ Status: {result['status']}")
            print(f"📊 Confidence: {result['confidence']}%")
            print(f"🔧 Local Fix Applied: {result.get('local_fix_applied', False)}")
            
            print(f"\n🔍 ROOT CAUSE:")
            print(f"   {result['root_cause']}")
            
            if 'analysis' in result:
                print(f"\n📁 ANALYSIS:")
                print(f"   File: {result['analysis']['responsible_file']}")
                print(f"   Function: {result['analysis']['responsible_function']}")
                print(f"   Line: {result['analysis']['responsible_line']}")
                print(f"   Reasoning: {result['analysis']['reasoning'][:200]}...")
            
            if 'fix' in result:
                print(f"\n💡 FIX GENERATED:")
                print(f"   Summary: {result['fix']['change_summary']}")
                print(f"   Lines changed: {result['fix']['lines_changed']}")
                print(f"   Confidence: {result['fix']['confidence_score']}%")
                print(f"   Test suggestion: {result['fix']['test_suggestion'][:150]}...")
                print(f"\n   Code preview:")
                print(f"   {result['fix']['fixed_code'][:300]}...")
            
            print("\n" + "="*60)
            
            if result.get('local_fix_applied'):
                print("\n✅ SUCCESS! Fix has been applied to your local file!")
                print("   Check: /Users/jaiaggarwal/drizz-tm-backend/reporting/html_report.py")
                print("   You can now review the changes with 'git diff'")
            else:
                print("\n⚠️  Fix generated but not applied (file may not exist)")
                
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_real_incident()
