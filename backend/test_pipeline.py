import qrcode
import requests
import time

# This ID matches one of the seed records in your DB
TEST_ID = "SEED9523-1"  

print(f"Generating QR Code for ID: {TEST_ID}", flush=True)
qr_img = qrcode.make(f"https://meditrace.com/verify?id={TEST_ID}")
img_path = "test_qr.jpg"
qr_img.save(img_path)

print(f"Dispatching POST request to /verify-image...", flush=True)
with open(img_path, "rb") as img_file:
    response = requests.post(
        "http://127.0.0.1:8000/verify-image", 
        files={"file": ("test_qr.jpg", img_file, "image/jpeg")}
    )

print(f"API Response (Status {response.status_code}):", flush=True)
result = response.json()
print(result, flush=True)

if result.get("status") == "processing":
    task_id = result["task_id"]
    print(f"\nPolling /verification/status/{task_id} for Celery completion...", flush=True)
    
    while True:
        status_resp = requests.get(f"http://127.0.0.1:8000/verification/status/{task_id}")
        status_data = status_resp.json()
        
        if status_data.get("status") == "processing":
            print("   Still processing...", flush=True)
            time.sleep(2)
        else:
            print("\nTask Complete! Final Worker Output:", flush=True)
            import json
            print(json.dumps(status_data, indent=2))
            break
