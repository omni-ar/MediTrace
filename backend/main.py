from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import qrcode
import os
import uuid

app = FastAPI()

# 1. CORS Setup (React Frontend ko allow karne ke liye)
origins = [
    "http://localhost:5173",  # React ka default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Folder jahan QR codes save honge
os.makedirs("qrcodes", exist_ok=True)

# 3. Static Files Mount (Taaki browser image dekh sake)
app.mount("/qrcodes", StaticFiles(directory="qrcodes"), name="qrcodes")

@app.get("/")
def read_root():
    return {"message": "MediTrace Backend is Running!"}

@app.get("/generate-batch/{drug_name}/{quantity}")
def generate_batch(drug_name: str, quantity: int):
    batch_id = str(uuid.uuid4())[:8]
    generated_files = []
    
    for i in range(quantity):
        unique_id = f"{batch_id}-{i+1}"
        data = f"MediTrace:{drug_name}:{unique_id}"
        
        # QR Image banana
        img = qrcode.make(data)
        file_name = f"{unique_id}.png"
        file_path = f"qrcodes/{file_name}"
        img.save(file_path)
        
        # Image ka URL return karna taaki React dikha sake
        generated_files.append(f"http://127.0.0.1:8000/qrcodes/{file_name}")
    
    return {
        "status": "Success",
        "batch_id": batch_id,
        "qr_codes": generated_files
    }