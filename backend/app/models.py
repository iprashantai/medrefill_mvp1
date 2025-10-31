"""
Database models for MedRefills AI using SQLModel.
"""
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum


class RefillStatus(str, Enum):
    """Status of a refill request."""
    PENDING_AI_REVIEW = "pending_ai_review"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    APPROVED = "approved"
    DENIED = "denied"


class Patient(SQLModel, table=True):
    """Patient model representing a patient in the EMR system."""
    __tablename__ = "patients"

    id: Optional[int] = Field(default=None, primary_key=True)
    mrn: str = Field(unique=True, index=True, description="Medical Record Number")
    first_name: str
    last_name: str
    date_of_birth: date
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    refill_requests: list["RefillRequest"] = Relationship(back_populates="patient")


class MedicationProtocol(SQLModel, table=True):
    """Protocol rules for medication refills."""
    __tablename__ = "medication_protocols"

    id: Optional[int] = Field(default=None, primary_key=True)
    medication_class: str = Field(index=True, description="e.g., 'SGLT2 Inhibitor', 'GLP-1 Agonist'")
    max_months_since_visit: Optional[int] = Field(
        default=None,
        description="Maximum months since last visit before requiring denial"
    )
    max_a1c_value: Optional[float] = Field(
        default=None,
        description="Maximum A1c value allowed (e.g., 8.0)"
    )
    require_recent_a1c: Optional[int] = Field(
        default=None,
        description="A1c must be within this many months"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    refill_requests: list["RefillRequest"] = Relationship(back_populates="protocol")


class RefillRequest(SQLModel, table=True):
    """Refill request record."""
    __tablename__ = "refill_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    protocol_id: int = Field(foreign_key="medication_protocols.id")
    
    status: RefillStatus = Field(default=RefillStatus.PENDING_AI_REVIEW)
    
    # AI decision data
    ai_decision: Optional[str] = Field(default=None, description="'Approve' or 'Deny'")
    ai_reason: Optional[str] = Field(default=None, description="Reasoning from AI")
    ai_confidence: Optional[float] = Field(default=None, description="Confidence score 0-100")
    
    # Human review data
    final_decision: Optional[str] = Field(default=None, description="Final decision after human review")
    reviewed_by: Optional[str] = Field(default=None, description="User ID of reviewer")
    reviewed_at: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    patient: Patient = Relationship(back_populates="refill_requests")
    protocol: MedicationProtocol = Relationship(back_populates="refill_requests")

