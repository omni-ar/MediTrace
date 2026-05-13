# MediTrace - Pharmaceutical Anti-Counterfeiting System

<div align="center">
  <img src="https://img.shields.io/badge/Status-100%25_Complete-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/YOLOv8-FF9900?style=for-the-badge" alt="YOLOv8" />
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" />
</div>

## Overview

**MediTrace** is an AI-powered blockchain-inspired pharmaceutical verification system that detects and traces counterfeit medicines through cryptographic serialization, supply chain tracking, and machine learning-based anomaly detection.

**Core Value Proposition:** Enable consumers to verify medicine authenticity and detect suspicious patterns by scanning a QR code, transforming counterfeit detection from reactive investigation to proactive surveillance.

## Project Status: 100% Complete

**Latest Milestone (May 13, 2026):** Production Security & Immutable Ledger Complete.

- **YOLOv8 Training:** 74.1% mAP50 (Authentic Validation Metric)
- **Random Forest:** 100% Test Accuracy
- **API & Security:** Stateless JWT, Live RBAC, Redis Rate Limiting
- **Blockchain:** Isolated Unit-Level Hash Chains (O(K) Verification)
- **Asynchronous ML:** Celery & Redis Worker Decoupling

---

## Project Vision

### The Problem

- **4,000 Crore INR** annual counterfeit drug market in India
- **10%** of drugs in developing countries are fake (WHO)
- **700,000 deaths** annually due to counterfeit medicines globally
- Zero consumer-side verification in current systems

### Our Solution

1. **Unit-Level Tracking** - Every single tablet receives a unique cryptographic hash (not batch-level)
2. **Zero-App Verification** - Scan QR → Browser opens → Instant result (works natively on any smartphone)
3. **Multi-Layer Detection** - Combines visual AI (YOLOv8) and behavioral ML (Random Forest)
4. **Isolated Hash Chains** - Cryptographic chaining ensures an immutable, tamper-proof audit trail

---

## Tech Stack

### Frontend

- **Framework**: React 18 with Vite
- **Styling**: Custom CSS with glass-morphism design principles
- **3D Graphics**: Three.js and React Three Fiber
- **Animations**: Framer Motion
- **State**: React Hooks (useState, useEffect)
- **Routing**: Single Page Application (SPA)

### Backend

- **Framework**: FastAPI (Python 3.11)
- **Database**: SQLAlchemy ORM (SQLite) and Alembic Migrations
- **Task Orchestration**: Celery
- **Message Broker**: Redis
- **Cryptography**: hashlib (SHA-256), passlib (bcrypt)
- **Security**: PyJWT (Stateless Authentication)

### Machine Learning / Deep Learning

- **Object Detection**: YOLOv8 (Ultralytics)
- **Classification**: Random Forest (scikit-learn)
- **Framework**: PyTorch 2.1.0

---

## Project Structure

```text
MediTrace/
├── frontend/                 # React SPA
│   ├── src/
│   │   ├── App.jsx          # Primary application views and 3D background
│   │   ├── VerifyPage.jsx   # Async-polling verification interface
│   │   ├── LedgerPage.jsx   # Blockchain ledger visualization
│   │   └── SystemMonitor.jsx # Real-time dashboard
│   └── package.json
│
├── backend/
│   ├── main.py              # API Gateway and asynchronous dispatch
│   ├── celery_app.py        # Celery configuration and Redis broker integration
│   ├── worker.py            # Asynchronous worker for ML inference execution
│   ├── security.py          # JWT, Passlib, and Role-Based Access Control routines
│   ├── blockchain.py        # Cryptographic Isolated Unit-Level Hash Chains logic
│   ├── database.py          # SQLAlchemy engine and session factory
│   ├── crud.py              # ORM database operations
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── alembic/             # Database migration configuration
│   ├── test_tampering.py    # Standalone script demonstrating live tamper defense
│   │
│   ├── ml_models/
│   │   ├── train_yolo.py             # YOLOv8 training script
│   │   ├── counterfeit_classifier.py # V2 Classifier with behavioral feature isolation
│   │
│   ├── trained_models/
│   │   └── yolov8_packaging.pt
│   │
│   ├── meditrace.db         # Primary SQLite database
│   └── requirements.txt
│
└── README.md                # This document
```

---

## Database Schema (Normalized)

**Note:** During the Phase 4 normalization, the redundant `ledger` table was dropped. The `supply_chain` table now serves as the single source of truth for the Immutable Ledger.

### 1. `users` Table
Stores authenticated system actors (manufacturers, administrators).
- **Columns:** `id`, `username`, `email`, `hashed_password`, `role`, `is_active`

### 2. `drugs` Table
Stores individual drug unit parameters and cryptographic hashes.
- **Columns:** `id`, `drug_name`, `generic_name`, `batch_id`, `unique_id` (UNIQUE), `hash` (UNIQUE), `manufacturer`, `license_number`, `dosage`, `composition`, `mrp`, `mfg_date`, `exp_date`, `created_at`

### 3. `supply_chain` Table (The Blockchain)
Tracks drug movement through the supply chain and mathematically locks events via consecutive hashing.
- **Columns:** `id`, `drug_id` (FK), `location`, `latitude`, `longitude`, `event_type`, `block_hash`, `previous_hash`, `timestamp`

### 4. `failed_attempts` Table
Logs counterfeit QR scans and system anomalies.
- **Columns:** `id`, `scanned_id`, `attempt_type`, `reason`, `ip_address`, `timestamp`

---

## System Architecture

### High-Level Event Flow

```text
┌─────────────────────────────────────────────────────────────┐
│                    USER JOURNEY                             │
└─────────────────────────────────────────────────────────────┘

1. MANUFACTURER
   |
   +-- Authenticates via JWT (Role: manufacturer)
   |
   +-- Backend generates:
       - Unique ID (ABC12345-1)
       - Genesis Block Hash (64 zeros)
       - QR code with resolution URL
   |
   +-- QR codes are printed and attached to packaging

2. SUPPLY CHAIN
   |
   +-- Drug transitions: Factory -> Warehouse -> Retail
   |
   +-- Each transition recorded in the database
   |
   +-- Isolated Hash Chain appends block via blockchain.py

3. CONSUMER
   |
   +-- Scans QR with native phone camera
   |
   +-- Browser automatically resolves: https://verify.meditrace.com/?id=ABC12345-1
   |
   +-- Heavy ML operations dispatched asynchronously to Celery/Redis
   |
   +-- Client polls for final analytical result
   |
   +-- Result displayed:
       [PASS] AUTHENTIC 
       [FAIL] COUNTERFEIT 
```

---

## Security Features

### 1. API Security: Stateless JWT and Live RBAC
- **Authentication:** Passwords are mathematically hashed utilizing `passlib` with `bcrypt`.
- **Stateless Tokens:** JSON Web Tokens (JWT) are restricted strictly to `sub` (User ID) and `exp` claims. The `role` claim is deliberately omitted to prevent the Stale Claims Vulnerability vector.
- **Live Database Check:** The `get_current_user` FastAPI dependency intercepts the JWT and performs a microsecond primary-key lookup to verify the user's `is_active` status. This guarantees instantaneous revocation of compromised accounts without awaiting token expiration.
- **Role-Based Access Control (RBAC):** Endpoints are protected by a `RequireRole` closure (e.g., `/generate-batch` is restricted to the `manufacturer` and `admin` roles).
- **Rate Limiting:** Public endpoints like `/verify-image` are throttled using a Redis-backed sliding window mechanism to deter Denial of Service (DoS) attacks.

### 2. Isolated Unit-Level Hash Chains (Immutable Ledger)
To circumvent the massive database lock contention (an $O(N)$ bottleneck) characteristic of global blockchains, MediTrace implements **Isolated Unit-Level Hash Chains**. Every individual drug unit strictly maintains its own discrete cryptographic ledger.

```text
Genesis Block (First Scan)
|- block_hash: 9d3077a9e9bfea8ac17e...
|- previous_hash: 0000000000000000000000000000000000000000000000000000000000000000 <- 64-Zero Genesis Root

Hop 1 (Warehouse Receipt)
|- block_hash: cd0a33257542657a1cb2...
|- previous_hash: 9d3077a9e9bfea8ac17e... <- Links to Genesis Block

Hop 2 (Retail Distribution)
|- block_hash: 58b73623c3c74fedc1aa...
|- previous_hash: cd0a33257542657a1cb2... <- Links to Hop 1
```

**Cryptographic Integrity:** Each hash calculation utilizes deterministic JSON serialization (`sort_keys=True`). If a bad actor alters a location row directly in the SQLite database, the entire chain instantly fractures during the $O(K)$ verification traversal.

### 3. Decoupled Machine Learning Pipeline
The machine learning architecture is physically decoupled from the API event loop to prevent blocking concurrent web requests.
When a client uploads an image, FastAPI assigns a UUID4 string, saves the image, and pushes the payload to the Redis broker. A background Celery worker consumes the task, executes the PyTorch/Scikit-learn inference matrices, and cleans up the temporary artifacts. The frontend client polls the `/verification/status/{task_id}` endpoint to retrieve the final resolution.

### 4. Geospatial Anomaly Detection (Haversine Formula)

```python
# Calculate great-circle distance
distance = haversine_distance(
    lat1=19.0760, lon1=72.8777,  # Mumbai
    lat2=28.7041, lon2=77.1025   # Delhi
)
# Result: 1153.24 km

# Calculate transit speed
speed = distance / time_hours

# Flag if mathematically impossible
if speed > 900:  # km/h (standard commercial airplane maximum speed)
    flag_as_cloning_attack()
```

---

## Machine Learning Pipeline Details

### YOLOv8: Visual Verification

**Training Specifications:**
- Epochs: 50
- Batch: 16
- Optimizer: AdamW (lr=0.001)

**Dataset Integrity:**
- Kaggle source: 7,800 pharmaceutical images
- Selected: 50 diverse samples
- Labeled: 49 on Roboflow (1 class: medicine_packaging)
- Augmentation: 3x (flip, rotate +/-15 degrees, brightness +/-15%, blur 1px)
- Final Structure: 147 images (76 train, 71 valid)

**Model Architecture:** YOLOv8-nano (3M params, 225 layers)

**Performance Benchmarks:**
| Metric | Value | Industry Standard | Evaluation Notes |
|---|---|---|---|
| Precision | 74.0% | >90% | On validation split |
| Recall | 75.6% | >85% | Zero critical misses |
| **mAP50** | **74.1%** | **>80%** | **Authentic Validation Metric (Epoch 21)** |
| Inference Latency | 112ms | <200ms | CPU-based execution |
| Payload Size | 6.3MB | <10MB | Suitable for edge-deployment |

**Artifact Repository:**
```text
trained_models/yolov8_packaging.pt (6.3 MB)
```

**Inference Execution:**
```python
from ultralytics import YOLO
model = YOLO('trained_models/yolov8_packaging.pt')
results = model('medicine.jpg')
```

---

### Random Forest Classifier

**Inference Results:**
```text
[PASS] Test Accuracy:  100%  (Perfect classification on isolated behavioral telemetry)
[PASS] Precision:      100%  (Zero false positives)
[PASS] Recall:         100%  (Zero false negatives)
[PASS] F1-Score:       100%  (Optimal balance)
[PASS] AUC-ROC:        100%  (Excellent discriminative capacity)
Artifact:              rf_behavioral_v2.pkl
```

**Dominant Telemetry Features:**
1. packaging_confidence (30.1% importance)
2. total_locations (22.9% importance)
3. recent_failures (12.3% importance)

**Prediction Matrix Output:**
```json
{
  "is_counterfeit": true,
  "confidence": 0.94,
  "risk_level": "CRITICAL",
  "recommendation": "DO NOT CONSUME"
}
```

---

## Setup and Installation Directives

### System Prerequisites
```bash
node --version  # Requires v18.0.0+
python --version  # Requires 3.11+
redis-server --version # Requires native Linux, WSL, or Docker instance
```

### Environment Configuration (.env)
Create a `.env` file in the `backend/` directory with the following minimum required variables before booting the system:
```env
# Cryptographic Keys
SECRET_KEY="your-secure-random-256-bit-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Infrastructure
DATABASE_URL="sqlite:///./meditrace.db"
REDIS_URL="redis://localhost:6379/0"
```

### Backend Initialization

**1. Clone Repository and Establish Environment**
```bash
git clone <repository-url>
cd MediTrace/backend
python -m venv venv
.\venv\Scripts\activate  # Windows Environments
source venv/bin/activate  # macOS/Linux Environments
pip install -r requirements.txt
```

**2. Boot Redis Message Broker (Docker Container)**
```bash
docker run -d -p 6379:6379 --name meditrace-redis redis:alpine
```

**3. Apply Database Migrations**
```bash
alembic upgrade head
python database.py
```

**4. Start the Background ML Worker**
Execute the following in an isolated terminal instance (with the virtual environment activated):
```bash
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

**5. Start the API Gateway**
Execute the following in an isolated terminal instance:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Initialization

```bash
cd ../frontend
npm install
npm run dev
```

---

## Version History

### v4.0.0 - May 13, 2026 (Current)
**Production Hardening and Immutable Ledger Integration**
- **Blockchain:** Re-architected system to utilize Isolated Unit-Level Hash Chains with strict deterministic JSON serialization (`sort_keys=True`).
- **Database Normalization:** Deleted redundant `ledger` table; merged auditing capabilities entirely into `supply_chain`.
- **Asynchronous Processing:** Decoupled PyTorch tensor inference from the FastAPI event loop using Celery workers and Redis.
- **Security Perimeter:** Introduced stateless JWT architecture, Live Database revocation queries, closure-based RBAC, and Edge Rate Limiting.

### v3.1.0 - Jan 15, 2026
**Architectural Hardening and Logic Overhaul**
- **Behavioral ML Core:** Migrated from Visual-dependence to a robust 10-point behavioral feature extraction framework.
- **Multi-Tier Classification:** Transitioned from Binary (Fake/Real) logic to Probabilistic Scoring (Authentic/Review/Suspicious).
- **Security Patch:** Implemented Salted SHA-256 Hashing arrays to mitigate potential rainbow table attacks.
- **Database Integrity:** Strictly enforced Foreign Key constraints and cascading deletion parameters.

### v3.0.0 - Jan 3, 2026
**ML Integration Milestone**
- Random Forest training complete (100% telemetry accuracy).
- End-to-end ML pipeline integrated with API endpoints.
- Live camera QR scanning functionality stabilized.

### v2.5.0 - Jan 2, 2026
**Visual Detection Release**
- YOLOv8 training routines completed successfully.
- Baseline model established: `yolov8_packaging.pt`.

### v2.0.0 - Dec 30, 2025
- Machine learning pipeline infrastructure established.
- Dataset preparation tooling integrated.
- System Monitor dashboard implemented.

### v1.0.0 - Dec 20, 2025
- Initial foundational release.
- Core validation logic deployed.
