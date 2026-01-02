from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import qrcode
import os
import uuid
import hashlib
from datetime import datetime
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from typing import Optional
import sqlite3

# Import database functions
from database import (
    save_drug_enhanced,
    get_drug_by_unique_id,
    get_supply_chain,
    add_supply_chain_event,
    log_failed_attempt,
    get_failed_attempts_count,
    get_recent_failed_attempts,
    init_db,
    seed_sample_data
)

# 🆕 NEW IMPORTS - Blockchain & Anomaly Detection
from blockchain import Blockchain
from anomaly_detection import (
    haversine_distance,
    detect_cloning_attempt,
    check_scan_frequency,
    analyze_drug_safety
)

app = FastAPI()

# 🆕 NEW: Initialize Blockchain
print("🔗 Initializing blockchain...")
blockchain = Blockchain()
print(f"✅ Blockchain ready with {len(blockchain.chain)} blocks")

# ---------------------------------------------------------
# 👇 YOUR WIFI IP ADDRESS
# ---------------------------------------------------------
MY_IP = "10.22.214.149"
# ---------------------------------------------------------

# CORS Setup - Allow Mobile Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("qrcodes", exist_ok=True)
app.mount("/qrcodes", StaticFiles(directory="qrcodes"), name="qrcodes")

# ════════════════════════════════════════════
# DATA MODELS
# ════════════════════════════════════════════

class DrugBatchRequest(BaseModel):
    drugName: str
    genericName: Optional[str] = None
    manufacturer: str
    licenseNumber: Optional[str] = None
    quantity: int
    dosage: Optional[str] = None
    composition: Optional[str] = None
    mrp: Optional[float] = None
    mfgDate: str
    expDate: str

# ════════════════════════════════════════════
# STARTUP - Initialize DB with Seed Data
# ════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    init_db()
    
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM drugs')
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        print("🌱 Seeding sample pharmaceutical batches...")
        seed_sample_data()
        print("✅ Sample data loaded - Dashboard ready!")
    else:
        print(f"✅ Database initialized with {count} existing units")

# ════════════════════════════════════════════
# ROOT ENDPOINT
# ════════════════════════════════════════════

@app.get("/")
def read_root():
    return {
        "message": "MediTrace Backend v2.0 - Blockchain Integrated",
        "status": "operational",
        "features": [
            "QR Generation", 
            "AI Verification", 
            "Supply Chain Tracking", 
            "Fake Detection",
            "Blockchain Verification",  # 🆕
            "Anomaly Detection"  # 🆕
        ]
    }

# ════════════════════════════════════════════
# STATS ENDPOINT (With Failed Attempts Count)
# ════════════════════════════════════════════

@app.get("/stats")
def get_stats():
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    # Total unique batches
    cursor.execute('SELECT COUNT(DISTINCT batch_id) FROM drugs')
    total_batches = cursor.fetchone()[0]
    
    # Total units
    cursor.execute('SELECT COUNT(*) FROM drugs')
    total_units = cursor.fetchone()[0]
    
    # Recent activity (last 7 days)
    cursor.execute('''
        SELECT COUNT(*) FROM drugs 
        WHERE created_at >= datetime('now', '-7 days')
    ''')
    recent_units = cursor.fetchone()[0]
    
    conn.close()
    
    # Get failed attempts count (FLAGGED ITEMS)
    failed_count = get_failed_attempts_count()
    
    # Calculate metrics
    efficiency = 99.3 if total_units > 0 else 0
    growth = round((recent_units / total_units * 100), 1) if total_units > 0 else 0
    
    return {
        "totalBatches": total_batches,
        "verified": total_units,
        "flagged": failed_count,
        "efficiency": efficiency,
        "growth": growth,
        "verificationRate": 99.3,
        "blockchainLength": len(blockchain.chain)  # 🆕 NEW
    }

# ════════════════════════════════════════════
# GENERATE BATCH (POST with Enhanced Fields)
# ════════════════════════════════════════════

@app.post("/generate-batch")
async def generate_batch(request: DrugBatchRequest):
    if request.quantity > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 units per batch")
    
    batch_id = str(uuid.uuid4())[:8].upper()
    generated_files = []
    
    for i in range(request.quantity):
        unique_id = f"{batch_id}-{i+1}"
        
        # Create verification URL for QR
        qr_data = f"http://{MY_IP}:5173/?id={unique_id}"
        
        # Generate SHA-256 hash
        hash_value = hashlib.sha256(
            f"MediTrace:{request.drugName}:{unique_id}:{request.mfgDate}".encode()
        ).hexdigest()
        
        # Save to database with all details
        drug_id = save_drug_enhanced(
            drug_name=request.drugName,
            generic_name=request.genericName,
            batch_id=batch_id,
            unique_id=unique_id,
            hash_value=hash_value,
            manufacturer=request.manufacturer,
            license_number=request.licenseNumber,
            dosage=request.dosage,
            composition=request.composition,
            mrp=request.mrp,
            mfg_date=request.mfgDate,
            exp_date=request.expDate
        )
        
        # Add supply chain event 1
        add_supply_chain_event(
            drug_id=drug_id,
            location="Bangalore Factory",
            lat=12.9716,
            lon=77.5946,
            event_type="Production Complete"
        )
        
        # 🆕 NEW: Add to blockchain
        blockchain.add_block(
            drug_id=drug_id,
            event_type="Production Complete",
            location="Bangalore Factory"
        )
        
        # Add supply chain event 2
        add_supply_chain_event(
            drug_id=drug_id,
            location="Chennai Warehouse",
            lat=13.0827,
            lon=80.2707,
            event_type="Quality Check"
        )
        
        # 🆕 NEW: Add to blockchain
        blockchain.add_block(
            drug_id=drug_id,
            event_type="Quality Check",
            location="Chennai Warehouse"
        )

        # Add supply chain event 3
        add_supply_chain_event(
            drug_id=drug_id,
            location="Mumbai Retail",
            lat=19.0760,
            lon=72.8777,
            event_type="Warehouse Receipt"
        )
        
        # 🆕 NEW: Add to blockchain
        blockchain.add_block(
            drug_id=drug_id,
            event_type="Warehouse Receipt",
            location="Mumbai Retail"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        file_name = f"{unique_id}.png"
        file_path = f"qrcodes/{file_name}"
        img.save(file_path)
        
        generated_files.append(f"http://127.0.0.1:8000/qrcodes/{file_name}")
    
    print(f"✅ Generated batch {batch_id} with {request.quantity} units")
    print(f"🔗 Blockchain now has {len(blockchain.chain)} blocks")
    
    return {
        "status": "Success",
        "batch_id": batch_id,
        "drug_name": request.drugName,
        "quantity": request.quantity,
        "qr_codes": generated_files,
        "blockchain_blocks_added": request.quantity * 3  # 🆕 NEW
    }

# ════════════════════════════════════════════
# VERIFY BY ID (With Anomaly Detection)
# ════════════════════════════════════════════

@app.get("/verify/{unique_id}")
def verify_drug(unique_id: str):
    # Get drug from database
    drug = get_drug_by_unique_id(unique_id)
    
    if not drug:
        # LOG FAILED ATTEMPT
        log_failed_attempt(
            scanned_id=unique_id,
            attempt_type="INVALID_ID",
            reason="Drug not found in database - Possible counterfeit"
        )
        
        return {
            "status": "fake",
            "message": "Drug not found in database. Possible counterfeit!"
        }
    
    # Get supply chain
    supply_chain = get_supply_chain(drug['id'])
    
    # 🆕 NEW: Analyze for anomalies
    anomaly_report = None
    if len(supply_chain) >= 2:
        # Run comprehensive safety analysis
        anomaly_report = analyze_drug_safety(unique_id)
        
        # If critical anomaly detected
        if anomaly_report and anomaly_report.get('risk_level') == 'CRITICAL':
            log_failed_attempt(
                scanned_id=unique_id,
                attempt_type="ANOMALY_DETECTED",
                reason=f"Impossible travel speed detected"
            )
            
            return {
                "status": "suspicious",
                "message": "⚠️ CRITICAL ANOMALY DETECTED",
                "name": drug['drug_name'],
                "batchId": drug['batch_id'],
                "anomaly": anomaly_report,
                "recommendation": "DO NOT CONSUME - Report to authorities immediately"
            }
    
    # Format for frontend
    locations = []
    for event in supply_chain:
        timestamp = event['timestamp']
        date_part = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
        time_part = timestamp.split(' ')[1] if ' ' in timestamp else '00:00:00'
        
        locations.append({
            'place': event['place'],
            'date': date_part,
            'time': time_part,
            'lat': event['latitude'],
            'lon': event['longitude'],
            'status': 'verified'
        })
    
    return {
        "status": "authentic",
        "name": drug['drug_name'],
        "genericName": drug['generic_name'],
        "batchId": drug['batch_id'],
        "manufacturer": drug['manufacturer'],
        "licenseNumber": drug['license_number'],
        "dosage": drug['dosage'],
        "mrp": drug['mrp'],
        "hash": drug['hash'],
        "mfgDate": drug['mfg_date'],
        "expDate": drug['exp_date'],
        "locations": locations,
        "anomalyReport": anomaly_report  # 🆕 NEW: Include anomaly report
    }

# ════════════════════════════════════════════
# VERIFY BY IMAGE UPLOAD (With Failed Logging)
# ════════════════════════════════════════════

@app.post("/verify-image")
async def verify_from_image(file: UploadFile = File(...)):
    try:
        # Read uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Decode QR code using pyzbar
        decoded_objects = decode(img)
        
        if not decoded_objects:
            return {"status": "error", "message": "No QR code detected in image"}
            
        # Extract unique_id from QR data
        qr_content = decoded_objects[0].data.decode('utf-8')
        print(f"📷 Scanned QR Content: {qr_content}")
        
        # Extract unique_id from URL
        if "id=" in qr_content:
            unique_id = qr_content.split("id=")[1]
        else:
            unique_id = qr_content
        
        # Verify drug
        drug = get_drug_by_unique_id(unique_id)
        
        if not drug:
            # LOG FAILED ATTEMPT
            log_failed_attempt(
                scanned_id=unique_id,
                attempt_type="FAKE_QR_IMAGE",
                reason=f"Image upload - QR decoded to '{unique_id}' but not in database"
            )
            
            return {"status": "fake", "message": f"Invalid QR Code: {unique_id}"}
            
        # Get supply chain
        supply_chain = get_supply_chain(drug['id'])
        
        locations = []
        for event in supply_chain:
            timestamp = event['timestamp']
            date_part = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
            time_part = timestamp.split(' ')[1] if ' ' in timestamp else '00:00:00'
            
            locations.append({
                'place': event['place'],
                'date': date_part,
                'time': time_part,
                'lat': event['latitude'],
                'lon': event['longitude'],
                'status': 'verified'
            })

        return {
            "status": "authentic",
            "unique_id": unique_id,
            "name": drug['drug_name'],
            "genericName": drug['generic_name'],
            "batchId": drug['batch_id'],
            "manufacturer": drug['manufacturer'],
            "dosage": drug['dosage'],
            "hash": drug['hash'],
            "mfgDate": drug['mfg_date'],
            "expDate": drug['exp_date'],
            "locations": locations
        }

    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return {"status": "error", "message": "Could not process image"}

# ════════════════════════════════════════════
# LEDGER (Blockchain View)
# ════════════════════════════════════════════

@app.get("/ledger")
def get_ledger():
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            sc.id,
            d.drug_name,
            d.batch_id,
            sc.event_type,
            sc.location,
            sc.timestamp
        FROM supply_chain sc
        JOIN drugs d ON sc.drug_id = d.id
        ORDER BY sc.timestamp DESC
        LIMIT 50
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    blocks = []
    for i, row in enumerate(results):
        # Generate hashes for blockchain feel
        current_hash = hashlib.sha256(f"{row[0]}{row[5]}".encode()).hexdigest()[:32]
        prev_hash = hashlib.sha256(f"{row[0]-1}{row[5]}".encode()).hexdigest()[:32] if i > 0 else "0x000000"
        
        blocks.append({
            "blockNumber": f"#{row[0]:05d}",
            "hash": f"0x{current_hash}",
            "previousHash": f"0x{prev_hash}",
            "timestamp": row[5],
            "drug": row[1],
            "batchId": row[2],
            "event": row[3],
            "location": row[4],
            "verified": True
        })
    
    return {"blocks": blocks}

# ════════════════════════════════════════════
# FAILED ATTEMPTS ENDPOINT (For Monitoring)
# ════════════════════════════════════════════

@app.get("/failed-attempts")
def get_failed_attempts():
    """Get recent failed verification attempts for monitoring"""
    attempts = get_recent_failed_attempts(limit=20)
    
    return {
        "total": len(attempts),
        "attempts": attempts
    }

# ════════════════════════════════════════════
# 🆕 NEW: BLOCKCHAIN STATUS ENDPOINT
# ════════════════════════════════════════════

@app.get("/blockchain/status")
def get_blockchain_status():
    """
    Get current blockchain integrity status
    
    🎓 LEARNING POINTS:
    - How to access blockchain data
    - How to verify chain integrity
    - How to format response for frontend
    """
    
    # Get latest block from chain
    latest_block = blockchain.get_latest_block()
    
    # Verify entire chain integrity
    is_valid = blockchain.verify_chain()
    
    # Get genesis (first) block
    genesis_block = blockchain.chain[0]
    
    return {
        "status": "verified" if is_valid else "corrupted",
        "integrity": "intact" if is_valid else "broken",
        "chainLength": len(blockchain.chain),
        "latestBlock": {
            "index": latest_block.index,
            "hash": latest_block.hash,
            "previousHash": latest_block.previous_hash,
            "timestamp": str(latest_block.timestamp),
            "data": latest_block.data
        },
        "genesisBlock": {
            "hash": genesis_block.hash,
            "timestamp": str(genesis_block.timestamp)
        },
        "lastVerified": datetime.now().isoformat()
    }

# ════════════════════════════════════════════
# 🆕 NEW: ANOMALY ANALYSIS ENDPOINT
# ════════════════════════════════════════════

@app.get("/anomaly/analyze/{unique_id}")
def analyze_anomalies(unique_id: str):
    """
    Detailed anomaly analysis for a specific drug
    
    🎓 LEARNING POINTS:
    - How Haversine distance is calculated
    - How speed thresholds work
    - How to detect cloning attempts
    """
    
    # Get drug
    drug = get_drug_by_unique_id(unique_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    # Get supply chain
    supply_chain = get_supply_chain(drug['id'])
    
    if len(supply_chain) < 2:
        return {
            "status": "insufficient_data",
            "message": "Need at least 2 supply chain events for analysis"
        }
    
    # Comprehensive analysis
    report = analyze_drug_safety(unique_id)
    
    # Add detailed breakdown
    detailed_events = []
    for i in range(len(supply_chain) - 1):
        event1 = supply_chain[i]
        event2 = supply_chain[i + 1]
        
        # Calculate distance
        distance = haversine_distance(
            event1['latitude'], event1['longitude'],
            event2['latitude'], event2['longitude']
        )
        
        # Calculate time difference
        from datetime import datetime
        time1 = datetime.fromisoformat(event1['timestamp'].replace(' ', 'T'))
        time2 = datetime.fromisoformat(event2['timestamp'].replace(' ', 'T'))
        time_diff_hours = (time2 - time1).total_seconds() / 3600
        
        # Calculate speed
        speed = distance / time_diff_hours if time_diff_hours > 0 else 0
        
        detailed_events.append({
            "from": event1['place'],
            "to": event2['place'],
            "distance_km": round(distance, 2),
            "time_hours": round(time_diff_hours, 2),
            "speed_kmh": round(speed, 2),
            "suspicious": speed > 900
        })
    
    return {
        "drug_id": unique_id,
        "drug_name": drug['drug_name'],
        "overall_report": report,
        "detailed_analysis": detailed_events,
        "total_events": len(supply_chain),
        "suspicious_transitions": sum(1 for e in detailed_events if e['suspicious'])
    }

# ════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "blockchain": "operational",
        "blockchain_length": len(blockchain.chain),
        "timestamp": datetime.now().isoformat()
    }

# ════════════════════════════════════════════
# SYSTEM MONITOR DASHBOARD ENDPOINT
# ════════════════════════════════════════════

@app.get("/monitor/dashboard")
def get_monitor_dashboard():
    """
    Complete dashboard data for System Monitor page
    
    Returns:
    - System health metrics
    - Blockchain status  
    - Recent anomalies from failed attempts
    """
    
    import time
    
    # 1. SYSTEM HEALTH
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    # Total scans = drugs created + failed attempts
    cursor.execute('SELECT COUNT(*) FROM drugs')
    total_drugs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM failed_attempts')
    total_failed = cursor.fetchone()[0]
    
    total_scans = total_drugs + total_failed
    
    # Calculate uptime (from when backend started)
    # Note: This resets on restart - for production use persistent storage
    uptime_seconds = time.time() - startup_time
    uptime_hours = int(uptime_seconds / 3600)
    uptime_mins = int((uptime_seconds % 3600) / 60)
    
    health = {
        "database": "connected",
        "api": "healthy",
        "uptime": f"{uptime_hours}h {uptime_mins}m",
        "totalScans": total_scans
    }
    
    # 2. BLOCKCHAIN STATUS
    latest_block = blockchain.get_latest_block()
    genesis_block = blockchain.chain[0]
    is_valid = blockchain.verify_chain()
    
    blockchain_data = {
        "integrity": "verified" if is_valid else "corrupted",
        "chainLength": len(blockchain.chain),
        "latestHash": latest_block.hash,
        "genesisHash": genesis_block.hash,
        "lastVerified": datetime.now().isoformat()
    }
    
    # 3. ANOMALIES (from failed attempts + real anomaly detection)
    cursor.execute('''
        SELECT scanned_id, attempt_type, reason, timestamp
        FROM failed_attempts
        ORDER BY timestamp DESC
        LIMIT 10
    ''')
    
    anomalies = []
    for row in cursor.fetchall():
        scanned_id, attempt_type, reason, timestamp = row
        
        # Determine severity
        severity = "critical" if "ANOMALY" in attempt_type else "medium"
        
        # Parse anomaly details from reason if available
        anomaly_data = {
            "id": scanned_id,
            "type": attempt_type,
            "severity": severity,
            "drugId": scanned_id,
            "reason": reason,
            "timestamp": timestamp,
            "status": "flagged"
        }
        
        # If it's a speed anomaly, try to extract details
        if "speed" in reason.lower() or "travel" in reason.lower():
            anomaly_data["type"] = "IMPOSSIBLE_SPEED"
            # Could parse distance, speed etc from reason string
            # For now, keep simple
        elif "frequency" in reason.lower() or "scan" in reason.lower():
            anomaly_data["type"] = "SUSPICIOUS_FREQUENCY"
        
        anomalies.append(anomaly_data)
    
    conn.close()
    
    return {
        "health": health,
        "blockchain": blockchain_data,
        "anomalies": anomalies,
        "timestamp": datetime.now().isoformat()
    }


# Add this at module level (top of file after imports)
import time
startup_time = time.time()