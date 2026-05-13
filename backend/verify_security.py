import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_step(msg):
    print(f"\n{'='*50}\n{msg}\n{'='*50}")

def run_tests():
    print_step("1. Registering Users")
    
    # Register Manufacturer
    mfg = {"username": "mfg_test", "password": "pass123", "role": "manufacturer"}
    res = requests.post(f"{BASE_URL}/auth/register", json=mfg)
    print(f"Manufacturer Registration: {res.status_code}")
    
    # Register Consumer
    consumer = {"username": "consumer_test", "password": "pass123", "role": "user"}
    res = requests.post(f"{BASE_URL}/auth/register", json=consumer)
    print(f"Consumer Registration: {res.status_code}")

    print_step("2. Getting Tokens (Login)")
    
    # Login Mfg
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "mfg_test", "password": "pass123"})
    mfg_token = res.json().get("access_token")
    print(f"Got Manufacturer Token: {mfg_token[:20]}...")
    
    # Login Consumer
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "consumer_test", "password": "pass123"})
    consumer_token = res.json().get("access_token")
    print(f"Got Consumer Token: {consumer_token[:20]}...")

    print_step("3. Testing RBAC on /generate-batch")
    
    payload = {
        "drug_name": "TestDrug", "manufacturer": "TestMfg", 
        "mfg_date": "2025-01-01", "exp_date": "2027-01-01", "quantity": 1
    }

    # Test 1: No Token
    res = requests.post(f"{BASE_URL}/generate-batch", json=payload)
    print(f"Test 1 (No Token): {res.status_code} -> {res.json()}")

    # Test 2: Consumer Token
    headers = {"Authorization": f"Bearer {consumer_token}"}
    res = requests.post(f"{BASE_URL}/generate-batch", json=payload, headers=headers)
    print(f"Test 2 (Consumer Token): {res.status_code} -> {res.json()}")

    # Test 3: Manufacturer Token
    headers = {"Authorization": f"Bearer {mfg_token}"}
    res = requests.post(f"{BASE_URL}/generate-batch", json=payload, headers=headers)
    print(f"Test 3 (Manufacturer Token): {res.status_code}")

if __name__ == "__main__":
    try:
        run_tests()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Is the FastAPI server running? Start it with 'uvicorn main:app'")
