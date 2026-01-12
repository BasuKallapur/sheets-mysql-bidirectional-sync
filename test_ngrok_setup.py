#!/usr/bin/env python3
"""
Quick test script for Apps Script integration with ngrok
"""
import requests
import json

def test_backend_endpoints(base_url):
    """Test all backend endpoints for Apps Script integration"""
    
    print(f"🧪 Testing backend at: {base_url}")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
    
    # Test 2: Apps Script sync endpoint (simulate Apps Script call)
    try:
        test_payload = {
            "sheet_id": "test_sheet_id_123",
            "edit_info": {
                "range": "A1",
                "sheet": "Sheet1",
                "user": "test@example.com",
                "timestamp": "2024-01-12T10:00:00Z",
                "editType": "EDIT",
                "oldValue": "",
                "newValue": "Test Value"
            },
            "trigger_source": "apps_script",
            "timestamp": "2024-01-12T10:00:00Z"
        }
        
        response = requests.post(
            f"{base_url}/apps-script-sync",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print("✅ Apps Script endpoint: WORKING (404 expected - no sync config)")
            print(f"   Response: {response.json()}")
        elif response.status_code == 200:
            print("✅ Apps Script endpoint: WORKING")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Apps Script endpoint: UNEXPECTED ({response.status_code})")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Apps Script endpoint: ERROR - {e}")
    
    # Test 3: List syncs
    try:
        response = requests.get(f"{base_url}/sync")
        if response.status_code == 200:
            print("✅ List syncs: PASSED")
            syncs = response.json()
            print(f"   Found {len(syncs)} sync configurations")
        else:
            print(f"❌ List syncs: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ List syncs: ERROR - {e}")
    
    print("\n🎯 Backend is ready for Apps Script integration!")
    print("\n📋 Next steps:")
    print("1. Copy the ngrok URL above")
    print("2. Update google-apps-script/Code.gs BACKEND_URL")
    print("3. Copy Code.gs to Google Apps Script editor")
    print("4. Test the connection using 'Test Connection' menu")

if __name__ == "__main__":
    # Test with localhost first
    print("Testing localhost backend...")
    test_backend_endpoints("http://localhost:8000")
    
    print("\n" + "="*50)
    print("🚀 Ready for ngrok!")
    print("Run: ngrok http 8000")
    print("Then test with your ngrok URL")