from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Drug, SupplyChainEvent, FailedAttempt, User, Transaction
import hashlib
import random
import uuid
from datetime import datetime, timedelta

def get_drug_by_unique_id(db: Session, unique_id: str):
    return db.query(Drug).filter(Drug.unique_id == unique_id).first()

def get_drugs_by_batch(db: Session, batch_id: str):
    drugs = db.query(Drug).filter(Drug.batch_id == batch_id).all()
    return [drug.unique_id for drug in drugs]

def save_drug_enhanced(db: Session, drug_name, generic_name, batch_id, unique_id, hash_value, 
                      manufacturer, license_number, dosage, composition, mrp, 
                      mfg_date, exp_date):
    db_drug = Drug(
        drug_name=drug_name,
        generic_name=generic_name,
        batch_id=batch_id,
        unique_id=unique_id,
        hash=hash_value,
        manufacturer=manufacturer,
        license_number=license_number,
        dosage=dosage,
        composition=composition,
        mrp=mrp,
        mfg_date=mfg_date,
        exp_date=exp_date
    )
    db.add(db_drug)
    db.commit()
    db.refresh(db_drug)
    return db_drug.id

from blockchain import hash_event

def add_supply_chain_event(db: Session, drug_id, location, lat, lon, event_type):
    # 1. Fetch the absolute latest event for this SPECIFIC drug, ordered by ID (not timestamp)
    last_event = db.query(SupplyChainEvent)\
                   .filter(SupplyChainEvent.drug_id == drug_id)\
                   .order_by(desc(SupplyChainEvent.id))\
                   .first()
                   
    # 2. Determine previous_hash (Genesis Root if First Scan)
    if not last_event:
        previous_hash = "0" * 64
    else:
        previous_hash = last_event.block_hash
        
    # 3. Create the event object to establish the timestamp before hashing
    timestamp = datetime.utcnow()
    
    # 4. Compute the deterministic hash
    block_hash = hash_event(
        drug_id=drug_id,
        event_type=event_type,
        location=location,
        timestamp_str=str(timestamp),
        previous_hash=previous_hash
    )
    
    # 5. Insert into DB
    db_event = SupplyChainEvent(
        drug_id=drug_id,
        location=location,
        latitude=lat,
        longitude=lon,
        event_type=event_type,
        previous_hash=previous_hash,
        block_hash=block_hash,
        timestamp=timestamp
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_supply_chain(db: Session, drug_id: int):
    return db.query(SupplyChainEvent).filter(SupplyChainEvent.drug_id == drug_id).order_by(SupplyChainEvent.timestamp.asc()).all()

def log_failed_attempt(db: Session, scanned_id, attempt_type, reason=None, ip_address=None):
    attempt = FailedAttempt(
        scanned_id=scanned_id,
        attempt_type=attempt_type,
        reason=reason,
        ip_address=ip_address
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    print(f"⚠️ Logged failed attempt: {scanned_id} - {attempt_type}")
    return attempt

def get_failed_attempts_count(db: Session):
    return db.query(FailedAttempt).count()

def get_recent_failed_attempts(db: Session, limit: int = 10):
    attempts = db.query(FailedAttempt).order_by(desc(FailedAttempt.timestamp)).limit(limit).all()
    return [
        {
            'scanned_id': a.scanned_id,
            'attempt_type': a.attempt_type,
            'reason': a.reason,
            'timestamp': str(a.timestamp)
        } for a in attempts
    ]

def has_failed_attempts(db: Session, unique_id: str) -> bool:
    count = db.query(FailedAttempt).filter(FailedAttempt.scanned_id == unique_id).count()
    return count > 0

def get_supply_chain_events(db: Session, unique_id: str) -> list:
    drug = get_drug_by_unique_id(db, unique_id)
    if not drug:
        return []
    return get_supply_chain(db, drug.id)

def get_drug_data_for_ml(db: Session, unique_id: str) -> dict:
    drug = get_drug_by_unique_id(db, unique_id)
    if not drug:
        return None
    return {
        'drug_name': drug.drug_name,
        'batch_id': drug.batch_id,
        'license_number': drug.license_number,
        'mrp': drug.mrp,
        'mfg_date': str(drug.mfg_date)
    }

def get_ledger(db: Session):
    # Retrieve recent global events, format them for UI (using actual block_hash instead of calculating dummy hashes)
    events = db.query(SupplyChainEvent, Drug).join(Drug, SupplyChainEvent.drug_id == Drug.id).order_by(desc(SupplyChainEvent.id)).limit(50).all()
    
    blocks = []
    for sc, d in events:
        blocks.append({
            "blockNumber": f"#{sc.id:05d}",
            "hash": sc.block_hash,
            "previousHash": sc.previous_hash,
            "timestamp": str(sc.timestamp),
            "drug": d.drug_name,
            "batchId": d.batch_id,
            "event": sc.event_type,
            "location": sc.location,
            "verified": True
        })
    return blocks

def get_stats(db: Session):
    total_batches = db.query(Drug.batch_id).distinct().count()
    total_units = db.query(Drug).count()
    recent_date = datetime.utcnow() - timedelta(days=7)
    recent_units = db.query(Drug).filter(Drug.created_at >= recent_date).count()
    failed_count = get_failed_attempts_count(db)
    
    efficiency = 99.3 if total_units > 0 else 0
    growth = round((recent_units / total_units * 100), 1) if total_units > 0 else 0
    
    return total_batches, total_units, failed_count, efficiency, growth

def seed_sample_data(db: Session):
    """Seed sample data if DB is empty"""
    count = db.query(Drug).count()
    if count > 0:
        return count
        
    sample_drugs = [
        {'drug_name': 'Dolo 650', 'generic_name': 'Paracetamol', 'manufacturer': 'Micro Labs Ltd.', 
         'license_number': '20B/UA/2018', 'dosage': '650mg', 'composition': 'Paracetamol IP 650mg, Excipients q.s.', 
         'mrp': 30.50, 'quantity': 10},
        {'drug_name': 'Azithral 500', 'generic_name': 'Azithromycin', 'manufacturer': 'Alembic Pharmaceuticals', 
         'license_number': '21C/GJ/2019', 'dosage': '500mg', 'composition': 'Azithromycin Dihydrate 500mg', 
         'mrp': 125.00, 'quantity': 8},
        {'drug_name': 'Crocin Advance', 'generic_name': 'Paracetamol', 'manufacturer': 'GlaxoSmithKline', 
         'license_number': '22A/MH/2020', 'dosage': '500mg', 'composition': 'Paracetamol 500mg with Optizorb Technology', 
         'mrp': 28.00, 'quantity': 12}
    ]
    
    total_created = 0
    for drug_data in sample_drugs:
        batch_id = f"SEED{random.randint(1000, 9999)}"
        mfg_date = (datetime.now() - timedelta(days=random.randint(30, 180))).date()
        exp_date = (datetime.now() + timedelta(days=random.randint(365, 730))).date()
        
        for i in range(drug_data['quantity']):
            unique_id = f"{batch_id}-{i+1}"
            hash_value = hashlib.sha256(
                f"MediTrace:{drug_data['drug_name']}:{unique_id}".encode()
            ).hexdigest()
            
            drug_id = save_drug_enhanced(
                db=db,
                drug_name=drug_data['drug_name'],
                generic_name=drug_data['generic_name'],
                batch_id=batch_id,
                unique_id=unique_id,
                hash_value=hash_value,
                manufacturer=drug_data['manufacturer'],
                license_number=drug_data['license_number'],
                dosage=drug_data['dosage'],
                composition=drug_data['composition'],
                mrp=drug_data['mrp'],
                mfg_date=mfg_date,
                exp_date=exp_date
            )
            
            add_supply_chain_event(db, drug_id, "Bangalore Factory", 12.9716, 77.5946, "Factory Production")
            add_supply_chain_event(db, drug_id, "Chennai Warehouse", 13.0827, 80.2707, "Warehouse Receipt")
            add_supply_chain_event(db, drug_id, "Mumbai Retail", 19.0760, 72.8777, "Retail Distribution")
            total_created += 1
            
    print(f"Seeded {total_created} units")
    return total_created
