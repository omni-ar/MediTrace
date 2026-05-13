import hashlib
import json
from datetime import datetime, timezone

def hash_event(drug_id: int, event_type: str, location: str, timestamp_str: str, previous_hash: str) -> str:
    """
    Cryptographic engine enforcing deterministic JSON serialization.
    """
    payload = {
        "drug_id": drug_id,
        "event_type": event_type,
        "location": location,
        "timestamp": timestamp_str,
        "previous_hash": previous_hash
    }
    
    # FATAL SERIALIZATION TRAP FIX:
    # Explicitly enforce key sorting and remove whitespace to guarantee 
    # identical byte-strings for the same dictionary payload.
    serialized_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    return hashlib.sha256(serialized_payload.encode('utf-8')).hexdigest()

def verify_drug_chain(events: list) -> bool:
    """
    Verifies the cryptographic chain of custody for a specific drug.
    Starts at the Genesis Root and recalculates every hash.
    Expects events ordered by insertion (ID ascending).
    """
    expected_previous = "0" * 64
    
    for event in events:
        # 1. Check if the chain link is broken
        if event.previous_hash != expected_previous:
            print(f"TAMPERING DETECTED: Broken link at Event {event.id}")
            return False
            
        # 2. Check if the block data itself was altered
        recalculated_hash = hash_event(
            drug_id=event.drug_id,
            event_type=event.event_type,
            location=event.location,
            timestamp_str=str(event.timestamp),
            previous_hash=event.previous_hash
        )
        
        if recalculated_hash != event.block_hash:
            print(f"TAMPERING DETECTED: Altered data at Event {event.id}")
            return False
            
        # 3. Update the expected tail for the next hop
        expected_previous = event.block_hash
        
    return True