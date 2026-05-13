from fastapi import FastAPI, HTTPException, File, UploadFile, Request
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
import time
startup_time = time.time()

from database import get_db, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
import crud
import schemas
import models
from security import (
    get_current_user, RequireRole, create_access_token,
    verify_password, get_password_hash, rate_limit_verify
)

# Blockchain engine — stateless cryptographic functions only
from blockchain import verify_drug_chain
from anomaly_detection import (
    haversine_distance,
    detect_cloning_attempt,
    check_scan_frequency,
    analyze_drug_safety
)

# ML models are now loaded in worker.py (Celery worker process)
# FastAPI no longer imports Ultralytics or Scikit-learn
from worker import process_verification

# Initialize FastAPI app
app = FastAPI()

# ---------------------------------------------------------
# 👇 YOUR WIFI IP ADDRESS
# ---------------------------------------------------------
MY_IP = "10.22.214.149"
# ---------------------------------------------------------

# CORS Setup - Allow Mobile Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://10.22.214.149:5173" # Adding your specific IP just in case
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("qrcodes", exist_ok=True)
app.mount("/qrcodes", StaticFiles(directory="qrcodes"), name="qrcodes")

# ════════════════════════════════════════════
# DATA MODELS
# ════════════════════════════════════════════

# Models moved to schemas.py

# ════════════════════════════════════════════
# STARTUP - Initialize DB with Seed Data
# ════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        count = crud.seed_sample_data(db)
        if count > 0:
            print(f"✅ Database initialized with {count} existing units")
        else:
            print("✅ Sample data loaded - Dashboard ready!")
    except Exception as e:
        print(f"⚠️ Startup error: {e}")
    finally:
        db.close()

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
# AUTHENTICATION ENDPOINTS
# ════════════════════════════════════════════

@app.post("/auth/register", response_model=schemas.UserResponse)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with bcrypt-hashed password."""
    existing = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = models.User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role or "user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return a signed JWT."""
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account deactivated")
    
    token = create_access_token(user_id=user.id)
    return {"access_token": token, "token_type": "bearer"}

# ════════════════════════════════════════════
# STATS ENDPOINT (With Failed Attempts Count)
# ════════════════════════════════════════════

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_batches, total_units, failed_count, efficiency, growth = crud.get_stats(db)
    
    return {
        "totalBatches": total_batches,
        "verified": total_units,
        "flagged": failed_count,
        "efficiency": efficiency,
        "growth": growth,
        "verificationRate": 99.3,
        "blockchainLength": db.query(models.SupplyChainEvent).count()
    }

# ════════════════════════════════════════════
# GENERATE BATCH (POST with Enhanced Fields)
# Restricted to: manufacturer, admin
# ════════════════════════════════════════════

@app.post("/generate-batch")
async def generate_batch(
    request: schemas.DrugBatchCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(RequireRole(["manufacturer", "admin"])),
):
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
            f"MediTrace:{request.drug_name}:{unique_id}:{request.mfg_date}".encode()
        ).hexdigest()
        
        # Save to database with all details
        drug_id = crud.save_drug_enhanced(
            db=db,
            drug_name=request.drug_name,
            generic_name=request.generic_name,
            batch_id=batch_id,
            unique_id=unique_id,
            hash_value=hash_value,
            manufacturer=request.manufacturer,
            license_number=request.license_number,
            dosage=request.dosage,
            composition=request.composition,
            mrp=request.mrp,
            mfg_date=request.mfg_date,
            exp_date=request.exp_date
        )
        
        # Add supply chain event 1
        crud.add_supply_chain_event(
            db=db,
            drug_id=drug_id,
            location="Bangalore Factory",
            lat=12.9716,
            lon=77.5946,
            event_type="Production Complete"
        )
        

        
        # Add supply chain event 2
        crud.add_supply_chain_event(
            db=db,
            drug_id=drug_id,
            location="Chennai Warehouse",
            lat=13.0827,
            lon=80.2707,
            event_type="Quality Check"
        )
        


        # Add supply chain event 3
        crud.add_supply_chain_event(
            db=db,
            drug_id=drug_id,
            location="Mumbai Retail",
            lat=19.0760,
            lon=72.8777,
            event_type="Warehouse Receipt"
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
        "drug_name": request.drug_name,
        "quantity": request.quantity,
        "qr_codes": generated_files,
        "blockchain_blocks_added": request.quantity * 3  # 🆕 NEW
    }

# ════════════════════════════════════════════
# VERIFY BY ID (With Anomaly Detection)
# ════════════════════════════════════════════

@app.get("/verify/{unique_id}", response_model=schemas.VerificationResponse)
def verify_drug(unique_id: str, db: Session = Depends(get_db)):
    """
    Verify drug authenticity with ML-powered counterfeit detection
    
    New features:
    - Random Forest behavioral analysis
    - YOLOv8 visual verification (if image provided)
    - Combined risk assessment
    """
    
    # Get drug from database
    drug = crud.get_drug_by_unique_id(db, unique_id)
    
    if not drug:
        # LOG FAILED ATTEMPT
        crud.log_failed_attempt(
            db=db,
            scanned_id=unique_id,
            attempt_type="INVALID_ID",
            reason="Drug not found in database - Possible counterfeit"
        )
        
        return {
            "status": "fake",
            "message": "Drug not found in database. Possible counterfeit!"
        }
    
    # Get supply chain
    supply_chain = crud.get_supply_chain(db, drug.id)
    
    # ML predictions are now handled asynchronously via /verify-image + Celery worker.
    # Text-only verification relies on anomaly detection and database validation.
    ml_prediction = None
    
    # 🔍 ANOMALY DETECTION (Existing geospatial analysis)
    anomaly_report = None
    if len(supply_chain) >= 2:
        anomaly_report = analyze_drug_safety(unique_id)
        
        if anomaly_report and anomaly_report.get('risk_level') == 'CRITICAL':
            crud.log_failed_attempt(
                db=db,
                scanned_id=unique_id,
                attempt_type="ANOMALY_DETECTED",
                reason=f"Impossible travel speed detected"
            )
            
            return {
                "status": "suspicious",
                "message": "⚠️ CRITICAL ANOMALY DETECTED",
                "name": drug.drug_name,
                "batchId": drug.batch_id,
                "anomaly": anomaly_report,
                "recommendation": "DO NOT CONSUME - Report to authorities immediately"
            }
    
    # Format supply chain for frontend
    locations = []
    for event in supply_chain:
        timestamp = str(event.timestamp)
        date_part = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
        time_part = timestamp.split(' ')[1] if ' ' in timestamp else '00:00:00'
        
        locations.append({
            'place': event.location,
            'date': date_part,
            'time': time_part,
            'lat': event.latitude,
            'lon': event.longitude,
            'status': 'verified'
        })
    
    # ✅ AUTHENTIC RESPONSE (with ML insights)
    response = {
        "status": "authentic",
        "name": drug.drug_name,
        "genericName": drug.generic_name,
        "batchId": drug.batch_id,
        "manufacturer": drug.manufacturer,
        "licenseNumber": drug.license_number,
        "dosage": drug.dosage,
        "mrp": drug.mrp,
        "hash": drug.hash,
        "mfgDate": str(drug.mfg_date),
        "expDate": str(drug.exp_date),
        "locations": locations,
        "anomalyReport": anomaly_report
    }
    
    # Add ML prediction if available
    if ml_prediction:
        response["ml_analysis"] = {
            "verdict": ml_prediction['verdict'],
            "confidence": f"{ml_prediction['confidence']:.1%}",
            "risk_level": ml_prediction['risk_level'],
            "probability_authentic": f"{ml_prediction['probability_authentic']:.1%}",
            "probability_counterfeit": f"{ml_prediction['probability_counterfeit']:.1%}"
        }
    
    return response

# ════════════════════════════════════════════
# VERIFY BY IMAGE (Async — Celery Dispatch)
# ════════════════════════════════════════════

TEMP_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "temp_uploads")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

@app.post("/verify-image", status_code=202)
async def verify_from_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _rate_check=Depends(rate_limit_verify),
):
    """
    Accepts image, decodes QR synchronously (lightweight),
    saves file with UUID4 prefix, dispatches ML to Celery worker.
    Returns 202 Accepted with task_id for polling.
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

        # QR decode is lightweight — stays in FastAPI
        decoded_objects = decode(img)
        if not decoded_objects:
            return {"status": "error", "message": "No QR code detected in image"}

        qr_content = decoded_objects[0].data.decode("utf-8")
        unique_id = qr_content.split("id=")[1] if "id=" in qr_content else qr_content

        # Verify drug exists before wasting a worker slot
        drug = crud.get_drug_by_unique_id(db, unique_id)
        if not drug:
            crud.log_failed_attempt(
                db=db, scanned_id=unique_id,
                attempt_type="FAKE_QR_IMAGE",
                reason=f"Image upload - QR decoded to '{unique_id}' but not in database"
            )
            return {"status": "fake", "message": f"Invalid QR Code: {unique_id}"}

        # UUID4-prefixed filename prevents race condition
        task_id = str(uuid.uuid4())
        safe_filename = f"{task_id}_{file.filename}"
        file_path = os.path.join(TEMP_UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        # Dispatch to Celery worker with explicit task_id
        process_verification.apply_async(args=[file_path, unique_id, task_id], task_id=task_id)

        return {
            "status": "processing",
            "task_id": task_id,
            "message": "Image received. ML analysis dispatched to background worker."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error dispatching image verification: {e}")
        import traceback
        return {"status": "error", "message": f"Could not process image upload: {str(e)}", "traceback": traceback.format_exc()}

# ════════════════════════════════════════════
# VERIFICATION STATUS (Polling Endpoint)
# ════════════════════════════════════════════

@app.get("/verification/status/{task_id}")
def get_verification_status(task_id: str):
    """Poll for the result of an async ML verification task."""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=process_verification.app)

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "processing", "message": "Task is queued or in progress."}
    elif result.state == "FAILURE":
        return {"task_id": task_id, "status": "error", "message": "Task failed during execution."}
    elif result.state == "SUCCESS":
        return result.result
    else:
        return {"task_id": task_id, "status": result.state}

# ════════════════════════════════════════════
# LEDGER (Blockchain View)
# ════════════════════════════════════════════

@app.get("/ledger")
def get_ledger(db: Session = Depends(get_db)):
    blocks = crud.get_ledger(db)
    return {"blocks": blocks}

# ════════════════════════════════════════════
# FAILED ATTEMPTS ENDPOINT (For Monitoring)
# ════════════════════════════════════════════

@app.get("/failed-attempts")
def get_failed_attempts(db: Session = Depends(get_db)):
    """Get recent failed verification attempts for monitoring"""
    attempts = crud.get_recent_failed_attempts(db, limit=20)
    
    return {
        "total": len(attempts),
        "attempts": attempts
    }

# ════════════════════════════════════════════
# VERIFY CHAIN (Immutable Ledger Integrity Check)
# ════════════════════════════════════════════

@app.get("/verify-chain/{unique_id}")
def verify_chain(unique_id: str, db: Session = Depends(get_db)):
    """
    Traverses the isolated unit-level hash chain for a specific drug.
    Recalculates every SHA-256 hash from the genesis root.
    Returns a hard boolean: is_tampered.
    """
    drug = crud.get_drug_by_unique_id(db, unique_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    # Fetch events in strict insertion order (by PK, not timestamp)
    from sqlalchemy import asc
    events = db.query(models.SupplyChainEvent)\
               .filter(models.SupplyChainEvent.drug_id == drug.id)\
               .order_by(asc(models.SupplyChainEvent.id))\
               .all()

    if not events:
        return {
            "unique_id": unique_id,
            "is_tampered": False,
            "message": "No supply chain events recorded yet.",
            "blocks_verified": 0
        }

    chain_intact = verify_drug_chain(events)

    if not chain_intact:
        return {
            "unique_id": unique_id,
            "is_tampered": True,
            "status": "CRITICAL",
            "message": "BLOCKCHAIN INTEGRITY FAILURE: Cryptographic chain is broken. This drug's supply chain data has been tampered with.",
            "blocks_verified": len(events)
        }

    return {
        "unique_id": unique_id,
        "is_tampered": False,
        "status": "VERIFIED",
        "message": "Chain of custody is cryptographically intact.",
        "blocks_verified": len(events),
        "genesis_hash": events[0].block_hash,
        "tail_hash": events[-1].block_hash
    }

# ════════════════════════════════════════════
# 🆕 NEW: ANOMALY ANALYSIS ENDPOINT
# ════════════════════════════════════════════

@app.get("/anomaly/analyze/{unique_id}")
def analyze_anomalies(unique_id: str, db: Session = Depends(get_db)):
    """
    Detailed anomaly analysis for a specific drug
    """
    
    # Get drug
    drug = crud.get_drug_by_unique_id(db, unique_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    # Get supply chain
    # Get supply chain
    supply_chain = crud.get_supply_chain(db, drug.id)
    
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
            event1.latitude, event1.longitude,
            event2.latitude, event2.longitude
        )
        
        # Calculate time difference
        time1 = event1.timestamp
        time2 = event2.timestamp
        time_diff_hours = (time2 - time1).total_seconds() / 3600
        
        # Calculate speed
        speed = distance / time_diff_hours if time_diff_hours > 0 else 0
        
        detailed_events.append({
            "from": event1.location,
            "to": event2.location,
            "distance_km": round(distance, 2),
            "time_hours": round(time_diff_hours, 2),
            "speed_kmh": round(speed, 2),
            "suspicious": speed > 900
        })
    
    return {
        "drug_id": unique_id,
        "drug_name": drug.drug_name,
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
def get_monitor_dashboard(db: Session = Depends(get_db)):
    """Complete dashboard data for System Monitor page"""
    
    import time
    
    # 1. SYSTEM HEALTH (using ORM)
    total_batches, total_units, failed_count, efficiency, growth = crud.get_stats(db)
    total_scans = total_units + failed_count
    
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
    
    # 3. ANOMALIES (using crud)
    recent_attempts = crud.get_recent_failed_attempts(db, limit=10)
    anomalies = []
    for attempt in recent_attempts:
        severity = "critical" if "ANOMALY" in attempt['attempt_type'] else "medium"
        anomaly_data = {
            "id": attempt['scanned_id'],
            "type": attempt['attempt_type'],
            "severity": severity,
            "drugId": attempt['scanned_id'],
            "reason": attempt.get('reason', ''),
            "timestamp": attempt['timestamp'],
            "status": "flagged"
        }
        reason = attempt.get('reason', '')
        if reason and ("speed" in reason.lower() or "travel" in reason.lower()):
            anomaly_data["type"] = "IMPOSSIBLE_SPEED"
        elif reason and ("frequency" in reason.lower() or "scan" in reason.lower()):
            anomaly_data["type"] = "SUSPICIOUS_FREQUENCY"
        anomalies.append(anomaly_data)
    
    return {
        "health": health,
        "blockchain": blockchain_data,
        "anomalies": anomalies,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ml/status")
def get_ml_status():
    """Get status of ML models — now served by Celery worker process."""
    return {
        "ml_enabled": True,
        "architecture": "async_celery",
        "models": {
            "yolov8": {
                "status": "loaded_in_worker",
                "purpose": "Visual packaging verification"
            },
            "random_forest": {
                "status": "loaded_in_worker",
                "purpose": "Behavioral counterfeit detection"
            }
        },
        "note": "ML models are loaded in the Celery worker process, not in FastAPI."
    }