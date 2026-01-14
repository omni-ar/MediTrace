import sqlite3
from datetime import datetime, timedelta
import hashlib
import random

def init_db():
    """Initialize database with enhanced schema including failed attempts tracking"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    # ENHANCED Drugs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT NOT NULL,
            generic_name TEXT,
            batch_id TEXT NOT NULL,
            unique_id TEXT UNIQUE NOT NULL,
            hash TEXT UNIQUE NOT NULL,
            manufacturer TEXT NOT NULL,
            license_number TEXT,
            dosage TEXT,
            composition TEXT,
            mrp REAL,
            mfg_date DATE NOT NULL,
            exp_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Supply Chain Events table WITH blockchain columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supply_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            event_type TEXT NOT NULL,
            block_hash TEXT,
            previous_hash TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drug_id) REFERENCES drugs(id)
        )
    ''')
    
    # Ledger table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            block_number INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE NOT NULL,
            previous_hash TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            drug_id INTEGER,
            event_type TEXT NOT NULL,
            location TEXT NOT NULL,
            verified BOOLEAN DEFAULT 1,
            FOREIGN KEY (drug_id) REFERENCES drugs(id)
        )
    ''')
    
    # Failed Attempts table (tracks fake QR scans)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS failed_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanned_id TEXT NOT NULL,
            attempt_type TEXT NOT NULL,
            reason TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def update_supply_chain_table():
    """Add blockchain hash columns to supply_chain table if they don't exist"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(supply_chain)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'block_hash' not in columns:
        cursor.execute('ALTER TABLE supply_chain ADD COLUMN block_hash TEXT')
        print("✅ Added block_hash column")
    
    if 'previous_hash' not in columns:
        cursor.execute('ALTER TABLE supply_chain ADD COLUMN previous_hash TEXT')
        print("✅ Added previous_hash column")
    
    conn.commit()
    conn.close()

def save_drug_enhanced(drug_name, generic_name, batch_id, unique_id, hash_value, 
                      manufacturer, license_number, dosage, composition, mrp, 
                      mfg_date, exp_date):
    """Save drug with all enhanced fields"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO drugs (
            drug_name, generic_name, batch_id, unique_id, hash,
            manufacturer, license_number, dosage, composition, mrp,
            mfg_date, exp_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        drug_name, generic_name, batch_id, unique_id, hash_value,
        manufacturer, license_number, dosage, composition, mrp,
        mfg_date, exp_date
    ))
    
    drug_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return drug_id

def get_drug_by_unique_id(unique_id):
    """Get drug with all details"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM drugs WHERE unique_id = ?', (unique_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'drug_name': result[1],
            'generic_name': result[2],
            'batch_id': result[3],
            'unique_id': result[4],
            'hash': result[5],
            'manufacturer': result[6],
            'license_number': result[7],
            'dosage': result[8],
            'composition': result[9],
            'mrp': result[10],
            'mfg_date': result[11],
            'exp_date': result[12]
        }
    return None

def log_failed_attempt(scanned_id, attempt_type, reason=None, ip_address=None):
    """Log a failed verification attempt (fake QR, invalid ID, etc.)"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO failed_attempts (scanned_id, attempt_type, reason, ip_address)
        VALUES (?, ?, ?, ?)
    ''', (scanned_id, attempt_type, reason, ip_address))
    
    conn.commit()
    conn.close()
    print(f"⚠️ Logged failed attempt: {scanned_id} - {attempt_type}")

def get_failed_attempts_count():
    """Get total count of failed verification attempts"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM failed_attempts')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def get_recent_failed_attempts(limit=10):
    """Get recent failed attempts for monitoring"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT scanned_id, attempt_type, reason, timestamp
        FROM failed_attempts
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'scanned_id': r[0],
            'attempt_type': r[1],
            'reason': r[2],
            'timestamp': r[3]
        }
        for r in results
    ]

def add_supply_chain_event(drug_id, location, lat, lon, event_type):
    """Add supply chain event"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO supply_chain (drug_id, location, latitude, longitude, event_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (drug_id, location, lat, lon, event_type))
    
    conn.commit()
    conn.close()

def get_supply_chain(drug_id):
    """Get supply chain history"""
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT location, latitude, longitude, event_type, timestamp 
        FROM supply_chain WHERE drug_id = ? ORDER BY timestamp ASC
    ''', (drug_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'place': r[0],
            'latitude': r[1],
            'longitude': r[2],
            'event_type': r[3],
            'timestamp': r[4]
        }
        for r in results
    ]

# ════════════════════════════════════════════
# SEED DATA - Professional Sample Batches
# ════════════════════════════════════════════

def seed_sample_data():
    """
    Create realistic sample batches for impressive dashboard.
    This runs only once when database is empty.
    """
    
    sample_drugs = [
        {'drug_name': 'Dolo 650', 'generic_name': 'Paracetamol', 'manufacturer': 'Micro Labs Ltd.', 
         'license_number': '20B/UA/2018', 'dosage': '650mg', 'composition': 'Paracetamol IP 650mg, Excipients q.s.', 
         'mrp': 30.50, 'quantity': 10},
        {'drug_name': 'Azithral 500', 'generic_name': 'Azithromycin', 'manufacturer': 'Alembic Pharmaceuticals', 
         'license_number': '21C/GJ/2019', 'dosage': '500mg', 'composition': 'Azithromycin Dihydrate 500mg', 
         'mrp': 125.00, 'quantity': 8},
        {'drug_name': 'Crocin Advance', 'generic_name': 'Paracetamol', 'manufacturer': 'GlaxoSmithKline', 
         'license_number': '22A/MH/2020', 'dosage': '500mg', 'composition': 'Paracetamol 500mg with Optizorb Technology', 
         'mrp': 28.00, 'quantity': 12},
        {'drug_name': 'Amoxyclav 625', 'generic_name': 'Amoxicillin + Clavulanic Acid', 'manufacturer': 'Cipla Ltd.', 
         'license_number': '19B/KA/2017', 'dosage': '625mg', 'composition': 'Amoxicillin 500mg + Clavulanic Acid 125mg', 
         'mrp': 180.00, 'quantity': 6},
        {'drug_name': 'Pantoprazole 40', 'generic_name': 'Pantoprazole', 'manufacturer': 'Sun Pharma', 
         'license_number': '23D/GJ/2021', 'dosage': '40mg', 'composition': 'Pantoprazole Sodium 40mg', 
         'mrp': 95.50, 'quantity': 15},
        {'drug_name': 'Cetirizine 10', 'generic_name': 'Cetirizine', 'manufacturer': 'Dr. Reddy\'s Labs', 
         'license_number': '20E/AP/2018', 'dosage': '10mg', 'composition': 'Cetirizine Dihydrochloride 10mg', 
         'mrp': 42.00, 'quantity': 20},
        {'drug_name': 'Combiflam', 'generic_name': 'Ibuprofen + Paracetamol', 'manufacturer': 'Sanofi India', 
         'license_number': '21F/MH/2019', 'dosage': '400mg+325mg', 'composition': 'Ibuprofen 400mg + Paracetamol 325mg', 
         'mrp': 35.00, 'quantity': 18}
    ]
    
    total_created = 0
    
    for drug_data in sample_drugs:
        batch_id = f"SEED{random.randint(1000, 9999)}"
        mfg_date = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
        exp_date = (datetime.now() + timedelta(days=random.randint(365, 730))).strftime('%Y-%m-%d')
        
        for i in range(drug_data['quantity']):
            unique_id = f"{batch_id}-{i+1}"
            hash_value = hashlib.sha256(
                f"MediTrace:{drug_data['drug_name']}:{unique_id}".encode()
            ).hexdigest()
            
            drug_id = save_drug_enhanced(
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
            
            # Add supply chain events
            add_supply_chain_event(
                drug_id=drug_id,
                location="Bangalore Factory",
                lat=12.9716,
                lon=77.5946,
                event_type="Production Complete"
            )
            
            add_supply_chain_event(
                drug_id=drug_id,
                location="Chennai Warehouse",
                lat=13.0827,
                lon=80.2707,
                event_type="Quality Check"
            )
            
            add_supply_chain_event(
                drug_id=drug_id,
                location="Mumbai Retail",
                lat=19.0760,
                lon=72.8777,
                event_type="Warehouse Receipt"
            )
            
            total_created += 1
    
    print(f"✅ Seeded {total_created} units across {len(sample_drugs)} batches")
    return total_created

if __name__ == '__main__':
    init_db()
    update_supply_chain_table()
    seed_sample_data()