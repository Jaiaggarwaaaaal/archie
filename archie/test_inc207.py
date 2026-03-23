#!/usr/bin/env python3
"""Test INC-207 incident investigation."""
import requests
import json
import sys

def test_inc207():
    """Send INC-207 to Archie."""
    
    incident_data = {
        "source": "manual",
        "title": "INC-207: No images in test report for thread yCmxs",
        "error_message": "Report for thread yCmxs shows no images. test_logs array truncated to steps 0-2, missing 151 steps including healing screenshots.",
        "severity": "minor",
        "timestamp": "2026-03-18T09:57:39Z",
        "environment": "production",
        "affected_service": "Enricher / Report Frontend",
        "details": {
            "thread_code": "yCmxs",
            "app": "com.aranoah.healthkart",
            "platform": "iOS BrowserStack",
            "test_start": "2026-03-17T18:20:53Z",
            "failed_at_step": 19,
            "root_cause_step": 18,
            "total_steps": 154,
            "test_logs_count": 3,
            "healing_screenshots": 20,
            "affected_files": [
                "report_generator.py",
                "step_logger.py",
                "healing_session.py"
            ],
            "stack_trace": "Step 18: LLM tapped container cell (element 8) instead of text input. Step 19 failed (UNDOABLE). Healing session EXEC_FAILED. Report generation pipeline truncated test_logs to steps 0-2.",
            "root_cause_analysis": "The test_logs array is being truncated during report generation.",
            "suggested_fixes": [
                "Fix test_logs truncation in report generation pipeline",
                "Surface healing screenshots in report UI"
            ]
        }
    }
    
    print("="*70)
    print("🔍 INVESTIGATING INC-207")
    print("="*70)
    print(f"\nIncident: {incident_data['title']}")
    print(f"Affected files: {', '.join(incident_data['details']['affected_files'])}")
    print(f"\nSending to Archie...")
    
    url = "http://localhost:8000/webhook/incident"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=incident_data, headers=headers, timeout=120)
        
        print(f"\n✅ Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*70)
            print("📊 INVESTIGATION RESULTS")
            print("="*70)
            
            print(f"\n🎯 Status: {result['status']}")
            print(f"📈 Confidence: {result['confidence']}%")
            print(f"💾 Local Fix Applied: {result.get('local_fix_applied', False)}")
            
            print(f"\n🔍 ROOT CAUSE:")
            print(f"   {result['root_cause']}")
            
            if 'analysis' in result:
                print(f"\n📁 DETAILED ANALYSIS:")
                print(f"   File: {result['analysis']['responsible_file']}")
                print(f"   Function: {result['analysis']['responsible_function']}")
                print(f"   Line: {result['analysis']['responsible_line']}")
                print(f"   Commit: {result['analysis'].get('responsible_commit', 'N/A')}")
                print(f"\n   Reasoning:")
                print(f"   {result['analysis']['reasoning'][:300]}...")
            
            if 'fix' in result:
                print(f"\n💡 GENERATED FIX:")
                print(f"   Summary: {result['fix']['change_summary']}")
                print(f"   Lines changed: {result['fix']['lines_changed']}")
                print(f"   Confidence: {result['fix']['confidence_score']}%")
                print(f"\n   Test suggestion:")
                print(f"   {result['fix']['test_suggestion'][:200]}...")
                
                if result.get('local_fix_applied'):
                    print(f"\n   📝 Code preview:")
                    print(f"   {result['fix']['fixed_code'][:400]}...")
            
            print("\n" + "="*70)
            
            if result.get('local_fix_applied'):
                print("\n✅ SUCCESS! Fix applied to your local repo!")
                print(f"   Check: /Users/jaiaggarwal/s_enricher/{result['analysis']['responsible_file']}")
                print("\n   Run 'git diff' to see changes")
            else:
                print("\n⚠️  Fix generated but not applied locally")
                
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out (investigation takes time with large codebases)")
        print("   Check Archie logs for progress")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_inc207()
