import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("----------------------------------------------------------------")
    print("1. Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

def test_final_response():
    print("\n----------------------------------------------------------------")
    print("2. Testing /api/v1/final-response (Main Agent)...")
    
    # Get user input at runtime
    user_q = input("Enter your travel query for the Agent (default: 'Venice Gondola'): ") or "Venice Gondola"
    
    payload = {
        "user_query": user_q
    }
    print(f"Sending payload: {payload}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/final-response", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response Preview: {data.get('response', '')[:200]}...") 
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")

def test_additional_info():
    print("\n----------------------------------------------------------------")
    print("3. Testing /api/v1/additional-info (Specific Info Agent)...")
    
    info_q = input("Enter query for Additional Info (default: 'Venice Gondola'): ") or "Venice Gondola"
    
    payload = {
        "query": info_q
    }
    print(f"Sending payload: {payload}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/additional-info", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Info Gathered: {data.get('info', '')[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Ensure 'python api.py' is running in another terminal!\n")
    test_health()
    test_final_response()
    test_additional_info()
