"""
Phase 4 Tampering Test
Proves the cryptographic perimeter actively detects database manipulation.
"""
import requests
import sqlite3
import os
import json

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = os.path.join(os.path.dirname(__file__), "meditrace.db")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def run_tampering_test():

    # ──────────────────────────────────────────────────────────
    # STEP 1: Find a real drug in the DB to use as test subject
    # ──────────────────────────────────────────────────────────
    print_section("STEP 1: Finding Test Subject")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.unique_id, sc.id, sc.location, sc.block_hash, sc.previous_hash
        FROM supply_chain sc
        JOIN drugs d ON sc.drug_id = d.id
        ORDER BY sc.id ASC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    if not rows:
        print("ERROR: No supply chain events in DB. Seed data first.")
        conn.close()
        return

    for r in rows:
        print(f"  unique_id={r[0]}, event_id={r[1]}, location={r[2]}")

    target_unique_id = rows[0][0]
    middle_event_id = rows[1][1] if len(rows) > 1 else rows[0][1]
    original_location = rows[1][2] if len(rows) > 1 else rows[0][2]

    print(f"\n  Target Drug : {target_unique_id}")
    print(f"  Will tamper : Event ID #{middle_event_id} | Location: '{original_location}'")

    # ──────────────────────────────────────────────────────────
    # STEP 2: Verify chain BEFORE tampering (should pass)
    # ──────────────────────────────────────────────────────────
    print_section("STEP 2: Chain Verification BEFORE Tampering")
    res = requests.get(f"{BASE_URL}/verify-chain/{target_unique_id}")
    print(f"  Status Code : {res.status_code}")
    print(f"  Response    : {json.dumps(res.json(), indent=4)}")
    assert res.json()["is_tampered"] == False, "ERROR: Chain should be intact before tampering!"
    print("\n  PASS — Chain is cryptographically intact.")

    # ──────────────────────────────────────────────────────────
    # STEP 3: Directly manipulate the SQLite database
    # ──────────────────────────────────────────────────────────
    print_section("STEP 3: Injecting Tampered Data into SQLite")
    fake_location = "FAKE CITY — Counterfeit Injection Point"
    cursor.execute(
        "UPDATE supply_chain SET location = ? WHERE id = ?",
        (fake_location, middle_event_id)
    )
    conn.commit()
    print(f"  Executed    : UPDATE supply_chain SET location='{fake_location}' WHERE id={middle_event_id}")
    
    # Verify the write landed
    cursor.execute("SELECT location FROM supply_chain WHERE id = ?", (middle_event_id,))
    stored = cursor.fetchone()[0]
    print(f"  DB confirms : location is now '{stored}'")
    conn.close()

    # ──────────────────────────────────────────────────────────
    # STEP 4: Hit the verify-chain endpoint AFTER tampering
    # ──────────────────────────────────────────────────────────
    print_section("STEP 4: Chain Verification AFTER Tampering")
    res = requests.get(f"{BASE_URL}/verify-chain/{target_unique_id}")
    print(f"  Status Code : {res.status_code}")
    response_json = res.json()
    print(f"  Response    :\n{json.dumps(response_json, indent=4)}")
    assert response_json["is_tampered"] == True, "CRITICAL FAILURE: Tampered chain was not detected!"
    print("\n  PASS — Blockchain perimeter detected the tampering attack.")

    # ──────────────────────────────────────────────────────────
    # STEP 5: Restore the original location
    # ──────────────────────────────────────────────────────────
    print_section("STEP 5: Restoring DB to Original State")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE supply_chain SET location = ? WHERE id = ?",
        (original_location, middle_event_id)
    )
    conn.commit()
    conn.close()
    print(f"  Restored    : Event #{middle_event_id} -> '{original_location}'")
    print("\n  Test complete. DB is clean.")

if __name__ == "__main__":
    try:
        run_tampering_test()
    except requests.exceptions.ConnectionError:
        print("ERROR: FastAPI server is not running. Start with 'uvicorn main:app --reload'")
