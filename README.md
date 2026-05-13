# MediTrace - Pharmaceutical Anti-Counterfeiting System

## 🎯 Overview

**MediTrace** is an AI-powered blockchain-inspired pharmaceutical verification system that **detects and traces** counterfeit medicines through cryptographic serialization, supply chain tracking, and machine learning-based anomaly detection.

**Core Value Proposition:** Enable consumers to **verify** medicine authenticity and **detect suspicious patterns** by scanning a QR code - transforming counterfeit detection from reactive investigation to proactive surveillance.

## 🚀 Project Status: 100% COMPLETE! 🎉

**Latest Milestone (Jan 3, 2026):** Full ML Integration Complete! 🚀

- ✅ YOLOv8 Training: 99.5% mAP50
- ✅ Random Forest: 100% Test Accuracy
- ✅ Live Camera Scanner: Fully Functional
- ✅ API Integration: Complete

---

## 🚀 Project Vision

### The Problem

- **₹4,000 Crore** annual counterfeit drug market in India
- **10%** of drugs in developing countries are fake (WHO)
- **7 lakh deaths** annually due to counterfeit medicines globally
- Zero consumer-side verification in current systems

### Our Solution

1. **Unit-Level Tracking** - Every single tablet gets unique cryptographic hash (not batch-level)
2. **Zero-App Verification** - Scan QR → Browser opens → Instant result (works on any phone)
3. **Multi-Layer Detection** - Combines visual AI (YOLOv8) + behavioral ML (Random Forest)
4. **Blockchain-Inspired** - Cryptographic chaining for tamper-proof audit trail

---

## 🏗️ Tech Stack

### Frontend

- **Framework**: React 18 with Vite
- **Styling**: Custom CSS with glass-morphism design
- **3D Graphics**: Three.js + React Three Fiber
- **Animations**: Framer Motion
- **State**: React Hooks (useState, useEffect)
- **Routing**: Single Page Application (SPA)

### Backend

- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLAlchemy ORM (SQLite for development, PostgreSQL-ready)
- **Task Orchestration**: Celery
- **Message Broker**: Redis
- **Cryptography**: hashlib (SHA-256)

### Machine Learning / Deep Learning

- **Object Detection**: YOLOv8 (Ultralytics)
- **Classification**: Random Forest (scikit-learn)
- **Framework**: PyTorch 2.1.0
- **Training**: Google Colab (GPU) or local CPU

### DevOps (Planned)

- **Containerization**: Docker (future)
- **Cloud**: AWS/Azure (future)
- **CI/CD**: GitHub Actions (future)

---

## 📁 Project Structure

```
MediTrace/
├── frontend/                 # React SPA
│   ├── src/
│   │   ├── App.jsx          # 4 tabs + 3D background
│   │   ├── VerifyPage.jsx   # 3 verification methods
│   │   ├── LedgerPage.jsx   # Blockchain view
│   │   └── SystemMonitor.jsx # Real-time dashboard
│   └── package.json
│
├── backend/
│   ├── main.py              # API Gateway and async dispatch
│   ├── celery_app.py        # Celery configuration and Redis broker integration
│   ├── worker.py            # Async worker for ML inference execution
│   ├── database.py          # SQLAlchemy engine and session factory
│   ├── crud.py              # ORM database operations
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── test_pipeline.py     # Automated end-to-end testing script
│   │
│   ├── ml_models/
│   │   ├── train_yolo.py             # YOLOv8 training script
│   │   ├── counterfeit_classifier.py # V2 Classifier with db_session integration
│   │
│   ├── trained_models/
│   │   └── yolov8_packaging.pt  # 6.3 MB
│   │
│   ├── dataset/
│   │   ├── raw/             # Kaggle 7,800 images
│   │   ├── selected/        # Curated 50
│   │   ├── train/           # 76 images + labels
│   │   ├── valid/           # 71 images + labels
│   │   └── data.yaml        # Config
│   │
│   ├── meditrace.db         # SQLite
│   ├── qrcodes/             # Generated QRs
│   └── requirements.txt
│
└── README.md                # This file
```

---

## 🗄️ Database Schema

### 1. `drugs` Table (13 columns)

**Purpose:** Stores individual drug unit information

| Column         | Type        | Description                         |
| -------------- | ----------- | ----------------------------------- |
| id             | INTEGER PK  | Auto-increment primary key          |
| drug_name      | TEXT        | Brand name (e.g., "Dolo 650")       |
| generic_name   | TEXT        | Generic name (e.g., "Paracetamol")  |
| batch_id       | TEXT        | Batch identifier (e.g., "ABC12345") |
| unique_id      | TEXT UNIQUE | Unit ID (e.g., "ABC12345-1")        |
| hash           | TEXT UNIQUE | SHA-256 cryptographic hash          |
| manufacturer   | TEXT        | Company name                        |
| license_number | TEXT        | Manufacturing license               |
| dosage         | TEXT        | Strength (e.g., "650mg")            |
| composition    | TEXT        | Chemical composition                |
| mrp            | REAL        | Maximum retail price                |
| mfg_date       | DATE        | Manufacturing date                  |
| exp_date       | DATE        | Expiry date                         |
| created_at     | TIMESTAMP   | Record creation time                |

### 2. `supply_chain` Table (10 columns)

**Purpose:** Tracks drug movement through supply chain

| Column        | Type       | Description          |
| ------------- | ---------- | -------------------- |
| id            | INTEGER PK | Auto-increment       |
| drug_id       | INTEGER FK | References drugs(id) |
| location      | TEXT       | Event location name  |
| latitude      | REAL       | GPS latitude         |
| longitude     | REAL       | GPS longitude        |
| event_type    | TEXT       | Event description    |
| block_hash    | TEXT       | Current block hash   |
| previous_hash | TEXT       | Previous block hash  |
| timestamp     | TIMESTAMP  | Event time           |

### 3. `failed_attempts` Table (6 columns)

**Purpose:** Logs fake QR scans and anomalies

| Column       | Type       | Description                                       |
| ------------ | ---------- | ------------------------------------------------- |
| id           | INTEGER PK | Auto-increment                                    |
| scanned_id   | TEXT       | QR code ID scanned                                |
| attempt_type | TEXT       | "INVALID_ID", "FAKE_QR_IMAGE", "ANOMALY_DETECTED" |
| reason       | TEXT       | Detailed reason for failure                       |
| ip_address   | TEXT       | User IP (optional)                                |
| timestamp    | TIMESTAMP  | Detection time                                    |

### 4. `ledger` Table (8 columns)

**Purpose:** Blockchain-style audit trail

| Column        | Type        | Description             |
| ------------- | ----------- | ----------------------- |
| block_number  | INTEGER PK  | Sequential block number |
| hash          | TEXT UNIQUE | Block hash              |
| previous_hash | TEXT        | Links to previous block |
| timestamp     | TIMESTAMP   | Block creation time     |
| drug_id       | INTEGER FK  | References drugs(id)    |
| event_type    | TEXT        | Event description       |
| location      | TEXT        | Event location          |
| verified      | BOOLEAN     | Verification status     |

---

## 🔄 System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER JOURNEY                             │
└─────────────────────────────────────────────────────────────┘

1. MANUFACTURER
   ↓
   Fills enhanced form (10 fields)
   ↓
   Backend generates:
   - Unique ID (ABC12345-1)
   - SHA-256 hash
   - QR code with URL
   ↓
   QR codes printed & attached to packaging

2. SUPPLY CHAIN
   ↓
   Drug moves: Factory → Warehouse → Retail
   ↓
   Each location recorded in database
   ↓
   GPS + timestamp captured
   ↓
   Blockchain blocks created

3. CONSUMER
   ↓
   Scans QR with phone camera
   ↓
   Browser auto-opens: http://IP:5173/?id=ABC12345-1
   ↓
   Frontend auto-verifies
   ↓
   Backend handles:
   - Fast verification (Database & Supply chain checks)
   - Heavy ML operations dispatched asynchronously to Celery/Redis
   - Client polls for final result
   ↓
   Result displayed:
   ✅ AUTHENTIC (green banner)
   ❌ COUNTERFEIT (red banner)
   ⚠️ SUSPICIOUS (yellow banner)
```

---

## 🔐 Security Features

### 1. API Security: Stateless JWT & Live RBAC

- **Authentication:** Passwords are hashed using `passlib` with `bcrypt`. 
- **Stateless Tokens:** JSON Web Tokens (JWT) are strictly scoped to `sub` (User ID) and `exp` claims. The `role` claim is deliberately omitted to prevent the Stale Claims Vulnerability.
- **Live Database Check:** The `get_current_user` FastAPI dependency intercepts the JWT and performs a microsecond primary-key lookup to verify the user's `is_active` status. This allows instantaneous revocation of compromised accounts without waiting for the token to expire.
- **Role-Based Access Control (RBAC):** Endpoints are protected by a `RequireRole` closure (e.g., `/generate-batch` restricted to `manufacturer` and `admin`).
- **Rate Limiting:** Public endpoints like `/verify-image` are throttled using a Redis-backed sliding window (e.g., 5 requests per 60 seconds per IP).

### 2. Cryptographic Hashing (SHA-256)

```python
hash_value = hashlib.sha256(
    f"MediTrace:{drug_name}:{unique_id}:{mfg_date}".encode()
).hexdigest()

# Example output:
# a3f8c9d2e1b4f7a6c8e9d2b5f8a3c6e9f1d4b7a2c5e8d1b4f7a0c3e6d9b2f5a8
```

**Purpose:** Tamper-proof fingerprint of each drug unit

### 3. Isolated Unit-Level Hash Chains (Immutable Ledger)

To avoid the massive database lock contention ($O(N)$ bottleneck) of a single global blockchain, MediTrace implements **Isolated Unit-Level Hash Chains**. Every individual drug unit maintains its own separate cryptographic ledger.

```
Genesis Block (First Scan)
├─ block_hash: 9d3077a9e9bfea8ac17e...
└─ previous_hash: 0000000000000000000000000000000000000000000000000000000000000000 ← 64-Zero Genesis Root

Hop 1 (Warehouse Receipt)
├─ block_hash: cd0a33257542657a1cb2...
└─ previous_hash: 9d3077a9e9bfea8ac17e... ← Links to Genesis!

Hop 2 (Retail Distribution)
├─ block_hash: 58b73623c3c74fedc1aa...
└─ previous_hash: cd0a33257542657a1cb2... ← Links to Hop 1!
```

**Cryptographic Integrity:** Each hash uses deterministic JSON serialization (`sort_keys=True`). If a bad actor alters a location row in the SQLite database, the entire chain instantly breaks during the $O(K)$ verification traversal.

### 4. Geospatial Anomaly Detection (Haversine Formula)

```python
#Calculate great-circle distance
distance = haversine_distance(
    lat1=19.0760, lon1=72.8777,  # Mumbai
    lat2=28.7041, lon2=77.1025   # Delhi
)
# Result: 1153.24 km

# Calculate speed
speed = distance / time_hours

# Flag if impossible
if speed > 900:  # km/h (max airplane speed)
    flag_as_cloning_attack()
```

### ⚠️ Current Limitations

**Blockchain Implementation:**

- **Current:** Cryptographic chaining in centralized SQLite database
- **Limitation:** Admin with database access can theoretically tamper
- **Immutability:** Achieved through hash validation, not decentralization
- **Production Requirement:** Migrate to Hyperledger Fabric or similar for true immutability

**Trade-offs:**

- ✅ Faster development and prototyping
- ✅ Lower infrastructure cost
- ✅ Demonstrates cryptographic concepts## 🛡️ Security Analysis

### Known Attack Vectors

#### 1. Photocopy/Clone Attack

**Attack:** Photocopy real QR code, attach to counterfeit products

**Current Mitigation:**

- ✅ Anomaly detection flags multiple scans from different locations
- ✅ Impossible speed detection (1000+ km/h between scans)
- ✅ Scan frequency analysis
- ⚠️ **Limitation:** First scan of cloned QR will pass

**Future Mitigation:**

- 🔄 Dynamic QR with OTP (changes every 30 seconds)
- 📱 NFC tags (unclonable)
- 🌐 Real-time scan coordination (reject simultaneous scans)

#### 2. Database Tampering

**Attack:** Admin access to modify SQLite records

**Current Mitigation:**

- ✅ Cryptographic hash validation
- ✅ Chain linking (tampering breaks chain)
- ⚠️ **Limitation:** Centralized database vulnerable

**Future Mitigation:**

- 🔗 Hyperledger Fabric (distributed ledger)
- 🔐 Multi-signature authorization
- 📊 Audit logging

### Honest Assessment

**What We Prevent:**

- ✅ Completely fake QR codes (not in database)
- ✅ Cloned QRs after first detection (anomaly flagging)
- ✅ Supply chain manipulation (hash mismatches)

**What We Detect (Not Prevent):**

- 🔍 First use of cloned QR (detection, not prevention)
- 🔍 Suspicious patterns (multiple rapid scans)

**Messaging Update:**

- ❌ Don't say: "Eliminates counterfeit drugs"
- ✅ Say: "Detects and traces counterfeit drugs, enabling rapid response"
- ⚠️ Not truly tamper-proof without decentralization

```

---


## 🤖 ML Pipeline Details

### YOLOv8: Visual Verification ✅ DONE

**Training:**

- Epochs: 50
- Batch: 16
- Optimizer: AdamW (lr=0.001)
- Time: 33 min 10 sec
- Device: AMD Ryzen 7 5800H (CPU)

**Dataset:**

- Kaggle source: 7,800 pharma images
- Selected: 50 diverse samples
- Labeled: 49 on Roboflow (1 class: medicine_packaging)
- Augmentation: 3x (flip, rotate ±15°, brightness ±15%, blur 1px)
- Final: 147 images (76 train, 71 valid)

**Model:** YOLOv8-nano (3M params, 225 layers)

**Performance:**
| Epoch | mAP50 | Precision | Recall |
|-------|-------|-----------|--------|
| 1 | 43.3% | 1.4% | 98.6% |
| 10 | 77.7% | 75.2% | 84.7% |
| 20 | 83.2% | 75.8% | 82.5% |
| 30 | 98.9% | 97.2% | 98.6% |
| **50** | **99.5%** | **99.7%** | **100%** |

**Files:**

```

trained_models/yolov8_packaging.pt (6.3 MB)
ml_models/runs/train/meditrace_packaging/
├── weights/best.pt
├── results.png
├── confusion_matrix.png
├── PR_curve.png
└── F1_curve.png

````

**Inference:**

```python
from ultralytics import YOLO
model = YOLO('trained_models/yolov8_packaging.pt')
results = model('medicine.jpg')
# Output: confidence=0.985, bbox=[45,67,580,635]
````

---

### Random Forest Classifier ✅

**Training Completed:** Jan 3, 2026, 11:30 PM

**Results:**

```
✅ Test Accuracy:  100%  (Perfect classification!)
✅ Precision:      100%  (Zero false positives)
✅ Recall:         100%  (Zero false negatives)
✅ F1-Score:       100%  (Perfect balance)
✅ AUC-ROC:        100%  (Excellent discrimination)
🔄 Cross-Val:      97.4% (5-fold, ±0.0%)
⏱️  Training:      <1 second
📦 Model:          12 KB (rf_classifier.pkl)
```

**Top 3 Features:**

1. packaging_confidence (30.1%)
2. total_locations (22.9%)
3. recent_failures (12.3%)
   💾 Model: 6.3 MB

````

**Training Plan:**

- Synthetic data: 40 authentic + 35 fake samples
- Algorithm: Random Forest (100 trees, max_depth=10)
- Split: 70/20/10 train/val/test
- Expected accuracy: 92-95%

**Prediction Output:**

```json
{
  "is_counterfeit": true,
  "confidence": 0.94,
  "risk_level": "CRITICAL",
  "recommendation": "DO NOT CONSUME"
}
````

### ⚠️ Important Note on Metrics

**Dataset Limitations:**

- Training Dataset: 75 synthetic samples (controlled scenarios)
- YOLOv8 Dataset: 147 images (augmented from 49 hand-labeled)
- High accuracy metrics reflect performance on limited, controlled data

**Real-World Expectations:**

- Current: 100% RF accuracy, 99.5% YOLOv8 mAP (proof-of-concept)
- Production: Expected 92-96% with diverse real-world conditions
- Challenges: Lighting variations, blur, damaged packaging, photocopies

**Why Such High Metrics?**

1. Small, curated dataset (quality over quantity)
2. Transfer learning from pre-trained YOLOv8 weights
3. Controlled synthetic data for Random Forest
4. Proof-of-concept phase, not production deployment

**Next Steps for Production:**

- Expand to 500+ real-world images
- Include edge cases and challenging scenarios
- Continuous learning from field deployment
- A/B testing with lower confidence thresholds

````

---

## 📡 API Endpoints

### Drug Management

#### `POST /generate-batch`

**Purpose:** Generate new drug batch with QR codes

**Request:**

```json
{
  "drugName": "Dolo 650",
  "genericName": "Paracetamol",
  "manufacturer": "Micro Labs Ltd.",
  "licenseNumber": "20B/UA/2018",
  "quantity": 5,
  "dosage": "650mg",
  "composition": "Paracetamol IP 650mg",
  "mrp": 30.5,
  "mfgDate": "2024-12-01",
  "expDate": "2026-12-01"
}
````

**Response:**

```json
{
  "status": "Success",
  "batch_id": "C28C623D",
  "drug_name": "Dolo 650",
  "quantity": 5,
  "qr_codes": [
    "http://localhost:8000/qrcodes/C28C623D-1.png",
    "http://localhost:8000/qrcodes/C28C623D-2.png",
    ...
  ],
  "blockchain_blocks_added": 15
}
```

---

#### `GET /verify/{unique_id}`

**Purpose:** Verify drug authenticity

**Example:** `GET /verify/C28C623D-1`

**Response (Authentic):**

```json
{
  "status": "authentic",
  "name": "Dolo 650",
  "genericName": "Paracetamol",
  "batchId": "C28C623D",
  "manufacturer": "Micro Labs Ltd.",
  "dosage": "650mg",
  "mrp": 30.50,
  "hash": "a3f8c9d2e1b4f7a6...",
  "mfgDate": "2024-12-01",
  "expDate": "2026-12-01",
  "locations": [
    {
      "place": "Bangalore Factory",
      "date": "2024-12-29",
      "time": "15:30:45",
      "lat": 12.9716,
      "lon": 77.5946,
      "status": "verified"
    },
    ...
  ],
  "anomalyReport": {
    "risk_level": "LOW",
    "anomalies_detected": false
  }
}
```

**Response (Fake):**

```json
{
  "status": "fake",
  "message": "Drug not found in database. Possible counterfeit!"
}
```

**Response (Suspicious):**

```json
{
  "status": "suspicious",
  "message": "⚠️ CRITICAL ANOMALY DETECTED",
  "name": "Dolo 650",
  "anomaly": {
    "type": "IMPOSSIBLE_SPEED",
    "risk_level": "CRITICAL",
    "details": {
      "from": "Mumbai",
      "to": "Delhi",
      "distance_km": 1153.24,
      "speed_kmh": 6919.45,
      "max_allowed": 900
    }
  },
  "recommendation": "DO NOT CONSUME - Report to authorities"
}
```

---

#### `POST /verify-image`

**Purpose:** Verify QR from uploaded image

**Request:** multipart/form-data with image file

**Response:** Same as `/verify/{unique_id}`

---

### Blockchain & Monitoring

#### `GET /blockchain/status`

**Purpose:** Get blockchain integrity status

**Response:**

```json
{
  "status": "verified",
  "integrity": "intact",
  "chainLength": 7,
  "latestBlock": {
    "index": 6,
    "hash": "b9f1f7c8859e6dbc...",
    "previousHash": "c8d1b4f7a0c3e6d9...",
    "timestamp": "2024-12-29T15:35:22",
    "data": {
      "drug_id": 92,
      "event_type": "Warehouse Receipt",
      "location": "Mumbai Retail"
    }
  },
  "genesisBlock": {
    "hash": "bea1e0522e9a2b86...",
    "timestamp": "2024-12-29T15:30:00"
  }
}
```

---

#### `GET /monitor/dashboard`

**Purpose:** Real-time system monitoring data

**Response:**

```json
{
  "health": {
    "database": "connected",
    "api": "healthy",
    "uptime": "48h 32m",
    "totalScans": 1247
  },
  "blockchain": {
    "integrity": "verified",
    "chainLength": 156,
    "latestHash": "b9f1f7c8...",
    "genesisHash": "bea1e052..."
  },
  "anomalies": [
    {
      "id": "C28C623D-1",
      "type": "ANOMALY_DETECTED",
      "severity": "critical",
      "drugId": "C28C623D-1",
      "reason": "Impossible travel speed detected",
      "timestamp": "2024-12-29T15:45:00"
    }
  ]
}
```

---

#### `GET /ledger`

**Purpose:** Get blockchain ledger view

**Response:**

```json
{
  "blocks": [
    {
      "blockNumber": "#00267",
      "hash": "0xb9f1f7c8859e6dbc",
      "previousHash": "0xe326814f6aebd005",
      "timestamp": "2024-12-29 15:35:22",
      "drug": "Dolo 650",
      "batchId": "C28C623D",
      "event": "Warehouse Receipt",
      "location": "Mumbai Retail",
      "verified": true
    },
    ...
  ]
}
```

---

#### `GET /stats`

**Purpose:** Dashboard statistics

**Response:**

```json
{
  "totalBatches": 8,
  "verified": 91,
  "flagged": 2,
  "efficiency": 99.3,
  "growth": 12.5,
  "verificationRate": 99.3,
  "blockchainLength": 7
}
```

---

#### `GET /anomaly/analyze/{unique_id}`

**Purpose:** Detailed anomaly analysis

**Response:**

```json
{
  "drug_id": "C28C623D-1",
  "drug_name": "Dolo 650",
  "overall_report": {
    "risk_level": "LOW",
    "cloning_alerts": [],
    "scan_frequency_alert": null
  },
  "detailed_analysis": [
    {
      "from": "Bangalore Factory",
      "to": "Chennai Warehouse",
      "distance_km": 290.52,
      "time_hours": 24.0,
      "speed_kmh": 12.1,
      "suspicious": false
    }
  ],
  "total_events": 3,
  "suspicious_transitions": 0
}
```

---

#### `GET /failed-attempts`

**Purpose:** Get failed verification attempts

**Response:**

```json
{
  "total": 2,
  "attempts": [
    {
      "scanned_id": "FAKE123-1",
      "attempt_type": "FAKE_QR_IMAGE",
      "reason": "QR decoded but not in database",
      "timestamp": "2024-12-29 15:30:00"
    },
    ...
  ]
}
```

---

#### `GET /health`

**Purpose:** System health check

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "blockchain": "operational",
  "blockchain_length": 7,
  "timestamp": "2024-12-29T15:45:22"
}
```

---

## 🚀 Setup & Installation

### Prerequisites

```bash
# Check versions
node --version  # v18.0.0+
python --version  # 3.10+
pip --version
npm --version
```

---

### Backend Setup

#### 1. Clone & Navigate

```bash
git clone <repository-url>
cd MediTrace/backend
```

#### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Core dependencies
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install qrcode[pil]==7.4.2
pip install opencv-python==4.8.1.78
pip install pyzbar==0.1.9
pip install numpy==1.26.2
pip install python-multipart==0.0.6
pip install Pillow==10.1.0

# 🆕 ML/DL dependencies
pip install ultralytics==8.1.0
pip install torch==2.1.0
pip install torchvision==0.16.0
pip install scikit-learn==1.3.2
pip install pandas==2.1.3
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install jupyter==1.0.0
pip install joblib==1.3.2

# Or use requirements.txt
pip install -r requirements.txt
```

#### 4. Initialize Database

```bash
python database.py
```

**Expected Output:**

```
✅ Database initialized successfully!
✅ Seeded 89 units across 7 batches
```

#### 5. Run Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**

```
🔗 Initializing blockchain...
✅ Blockchain ready with 1 blocks
✅ Database initialized with 89 existing units
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

### Frontend Setup

#### 1. Navigate to Frontend

```bash
cd ../frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Run Frontend

```bash
npm run dev
```

**Expected Output:**

```
VITE v5.0.0  ready in 523 ms

➜  Local:   http://localhost:5173/
➜  Network: http://10.205.204.149:5173/
```

---

### Access Application

**Frontend:** http://localhost:5173
**Backend API:** http://localhost:8000
**API Docs:** http://localhost:8000/docs (Swagger UI)

---

## 🧪 Testing

### Manual Testing Checklist

#### ✅ Dashboard

- [ ] Stats cards show correct numbers
- [ ] Form validation works
- [ ] QR generation successful
- [ ] QR images display in grid

#### ✅ Verify

- [ ] Manual ID entry works
- [ ] File upload works
- [ ] Camera scan works (if implemented)
- [ ] Supply chain timeline displays
- [ ] Fake ID shows red banner

#### ✅ Ledger

- [ ] All blocks displayed
- [ ] Search functionality works
- [ ] Filter by status works
- [ ] Hashes display correctly

#### ✅ Monitor

- [ ] Real-time data loads
- [ ] Blockchain status correct
- [ ] Anomalies display (if any)
- [ ] Auto-refresh (30 sec)

---

### API Testing

**Using curl:**

```bash
# Health check
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/stats

# Verify drug
curl http://localhost:8000/verify/C28C623D-1

# Blockchain status
curl http://localhost:8000/blockchain/status
```

---

## 📊 Current Status (As of January 2, 2026)

### ✅ Completed Features (95%)

#### Backend

- [x] FastAPI server with 11 endpoints
- [x] Enhanced drug registration (10 fields)
- [x] QR generation with URL embedding
- [x] SHA-256 cryptographic hashing
- [x] Supply chain tracking (3 events per drug)
- [x] Blockchain implementation (chain linking, tampering detection)
- [x] Haversine geospatial analysis
- [x] Anomaly detection (speed-based)
- [x] Failed attempt logging
- [x] Real-time statistics
- [x] Seed data (89 units, 7 batches)

#### Frontend

- [x] 4-tab navigation (Dashboard, Verify, Ledger, Monitor)
- [x] 3D DNA helix animation (Three.js)
- [x] Enhanced registration form (10 fields)
- [x] 3 verification methods (manual, upload, camera)
- [x] Supply chain timeline visualization
- [x] Blockchain ledger view
- [x] System monitoring dashboard
- [x] Real-time data integration
- [x] Responsive design
- [x] Glass-morphism UI

#### Database

- [x] 4 tables with proper relations
- [x] 89 seed records
- [x] Foreign keys configured
- [x] Indexes on unique_id, batch_id

---

### 🚧 In Progress (Current Work)

#### ML/DL Pipeline

- [x] YOLOv8 setup & testing
- [ ] Dataset labeling (0/50 images)
- [ ] YOLOv8 training
- [ ] Random Forest feature engineering
- [ ] Random Forest training
- [ ] Model integration with backend

---

### 📅 Planned Features (Future)

#### Phase 4: Production Hardening (Week 1-3)

- [ ] Migration: SQLite → PostgreSQL
- [ ] Add database indexes
- [ ] Implement caching (Redis)
- [ ] API rate limiting
- [ ] Error handling improvements
- [ ] Logging system

### Phase 5: Advanced Features (Future)

**Target Audience Clarification:**

**Consumers (End Users):**

- ✅ Zero-App Web Verification (Main USP - stays browser-based)
- No app download required
- Works on any smartphone

**Supply Chain Partners (Distributors/Regulators):**

- 📱 Mobile App (React Native) - for bulk scanning, offline mode
- Batch verification capabilities
- Warehouse integration
- Inventory management

**The "Zero-App" USP remains for end consumers. The mobile app targets business users.**

## 📈 Performance Benchmarks

**Update Performance Benchmarks:**

```markdown
### YOLOv8 Model

| Metric           | Value   | Industry  | Grade      | Notes                |
| ---------------- | ------- | --------- | ---------- | -------------------- |
| Precision        | 99.7%   | >90%      | ⭐⭐⭐⭐⭐ | On validation set    |
| Recall           | 100%    | >85%      | ⭐⭐⭐⭐⭐ | Zero misses          |
| mAP50            | 99.5%   | >80%      | ⭐⭐⭐⭐⭐ | Industry-leading     |
| mAP50-95         | 70.0%   | >50%      | ⭐⭐⭐⭐   | Good localization    |
| Inference        | 112ms   | <200ms    | ⭐⭐⭐⭐⭐ | CPU-based            |
| Model Size       | 6.3MB   | <10MB     | ⭐⭐⭐⭐⭐ | Edge-deployable      |
| **Dataset Size** | **147** | **1000+** | **⭐⭐**   | **Proof-of-concept** |
| **Real Images**  | **49**  | **500+**  | **⭐⭐**   | **+ Augmentation**   |
```

---

### System Performance

| Metric           | Value  | Target | Status |
| ---------------- | ------ | ------ | ------ |
| API Response     | <100ms | <200ms | ✅     |
| QR Generation    | 0.5s   | <1s    | ✅     |
| Verification     | 3s     | <5s    | ✅     |
| Concurrent Users | 50     | 100    | ✅     |

---

## 🔄 Version History

### v3.1.0 - Jan 15, 2026 (Current)

**Architectural Hardening & Logic Overhaul** 🛡️

- ✅ **Behavioral ML Core:** Switched from Visual-dependence to 10-point behavioral feature extraction.
- ✅ **Multi-Tier Classification:** Replaced Binary (Fake/Real) with Probabilistic Scoring (Authentic/Review/Suspicious).
- ✅ **Security Patch:** Implemented Salted SHA-256 Hashing to prevent rainbow table attacks.
- ✅ **Database Integrity:** Enforced Foreign Key constraints and cascading deletes.
- **Critical Fix:** Resolved false positives for manual ID entry (The "53% Confidence" bug).

### v3.0.0 - Jan 3, 2026

**ML Integration Complete** 🚀

- ✅ Random Forest training complete (100% accuracy)
- ✅ Full ML pipeline integrated
- ✅ Live camera QR scanning functional

### v2.5.0 - Jan 2, 2026

**ML/DL Milestone** ✨

- ✅ YOLOv8 training complete (99.5% mAP50)
- ✅ Model saved: `yolov8_packaging.pt`
- ✅ Training artifacts generated
- 🚧 Random Forest feature engineering started

### v2.0.0 - Dec 30, 2025

- ✨ ML/DL pipeline structure
- ✨ Dataset preparation tools
- 🔧 System Monitor dashboard

### v1.5.0 - Dec 25, 2025

- ✨ System Monitor page
- ✨ Failed attempt tracking
- 🐛 Blockchain integration fixes

### v1.0.0 - Dec 20, 2025

- 🎉 Initial release
- Core verification system

---

**Built with ❤️ by the Arjit Tripathi**

**Last Updated:** January 3, 2026
