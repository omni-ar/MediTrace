from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, date

# ==========================================
# USER SCHEMAS (Phase 5 Prep)
# ==========================================

class UserBase(BaseModel):
    username: str
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

# ==========================================
# TRANSACTION SCHEMAS (Generic Audit)
# ==========================================

class TransactionBase(BaseModel):
    item_id: str
    status: str
    qr_data: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# DRUG (MEDITRACE CORE) SCHEMAS
# ==========================================

class DrugBase(BaseModel):
    drug_name: str
    generic_name: Optional[str] = None
    manufacturer: str
    license_number: Optional[str] = None
    dosage: Optional[str] = None
    composition: Optional[str] = None
    mrp: Optional[float] = None
    mfg_date: date
    exp_date: date

class DrugBatchCreate(DrugBase):
    """Used for /generate-batch requests"""
    quantity: int = Field(..., gt=0, le=50, description="Max 50 units per batch")

class DrugResponse(DrugBase):
    id: int
    batch_id: str
    unique_id: str
    hash: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# SUPPLY CHAIN & LEDGER SCHEMAS
# ==========================================

class SupplyChainEventBase(BaseModel):
    location: str
    latitude: float
    longitude: float
    event_type: Literal[
        'Factory Production', 
        'Warehouse Receipt', 
        'Retail Distribution', 
        'Quality Check', 
        'Production Complete'
    ]

class SupplyChainEventResponse(SupplyChainEventBase):
    id: int
    drug_id: int
    block_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ML VERIFICATION ENVELOPE (Strict Envelope, Dynamic Payload)
# ==========================================

class VerificationResponse(BaseModel):
    """
    Implements the Strict Envelope, Dynamic Payload pattern.
    The envelope properties are strictly typed.
    The ML payload is a Dict[str, Any] to accommodate Ultralytics/Sklearn tensor changes.
    """
    status: Literal['authentic', 'fake', 'suspicious', 'error']
    message: Optional[str] = None
    unique_id: Optional[str] = None
    name: Optional[str] = None
    genericName: Optional[str] = None
    batchId: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage: Optional[str] = None
    hash: Optional[str] = None
    mfgDate: Optional[str] = None
    expDate: Optional[str] = None
    
    # Standard locations list for UI
    locations: Optional[List[Dict[str, Any]]] = None
    
    # ⚠️ ML Dynamic Payloads
    ml_analysis: Optional[Dict[str, Any]] = None
    visual_verification: Optional[Dict[str, Any]] = None
    anomalyReport: Optional[Dict[str, Any]] = None

    # CRITICAL: Prevent 500 Server Errors from Scikit-learn/PyTorch NaN and Inf edge cases
    model_config = ConfigDict(
        ser_json_inf_nan='constants',  # Serializes NaN/Inf to constants instead of crashing
        from_attributes=True
    )
