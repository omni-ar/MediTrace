from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class User(Base):
    """
    Phase 5 Security Foundation: JWT & RBAC
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user") # 'admin', 'manufacturer', 'user'
    is_active = Column(Boolean, default=True)  # Live revocation flag
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    """
    Generic Audit/Transaction Log
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(100), index=True, nullable=False)
    status = Column(String(50), nullable=False)
    qr_data = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Drug(Base):
    """
    Core Pharmaceutical Entity
    """
    __tablename__ = "drugs"
    
    id = Column(Integer, primary_key=True, index=True)
    drug_name = Column(String(100), nullable=False)
    generic_name = Column(String(100))
    batch_id = Column(String(50), index=True, nullable=False)
    unique_id = Column(String(100), unique=True, index=True, nullable=False)
    hash = Column(String(64), unique=True, nullable=False)
    
    manufacturer = Column(String(100), nullable=False)
    license_number = Column(String(50))
    dosage = Column(String(50))
    composition = Column(String(255))
    mrp = Column(Float)
    mfg_date = Column(Date, nullable=False)
    exp_date = Column(Date, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    supply_chain_events = relationship("SupplyChainEvent", back_populates="drug", cascade="all, delete-orphan")

class SupplyChainEvent(Base):
    """
    Geospatial supply chain tracking (V1 Behavior)
    """
    __tablename__ = "supply_chain"
    
    id = Column(Integer, primary_key=True, index=True)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=False)
    
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    event_type = Column(String(100), nullable=False)
    
    # Blockchain linkage
    block_hash = Column(String(64))
    previous_hash = Column(String(64))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    drug = relationship("Drug", back_populates="supply_chain_events")


class FailedAttempt(Base):
    """
    Tracks failed verification attempts (Fake QRs, ML Flags)
    """
    __tablename__ = "failed_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    scanned_id = Column(String(100), index=True, nullable=False)
    attempt_type = Column(String(100), nullable=False)
    reason = Column(String(255))
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
