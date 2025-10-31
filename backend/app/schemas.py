"""
Pydantic schemas for API data transfer.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class PatientRead(BaseModel):
    """Patient read schema."""
    id: int
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: date

    class Config:
        from_attributes = True


class MedicationProtocolRead(BaseModel):
    """Medication protocol read schema."""
    id: int
    medication_class: str
    max_months_since_visit: Optional[int] = None
    max_a1c_value: Optional[float] = None
    require_recent_a1c: Optional[int] = None

    class Config:
        from_attributes = True


class RefillRequestRead(BaseModel):
    """Refill request read schema."""
    id: int
    patient_id: int
    protocol_id: int
    status: str
    ai_decision: Optional[str] = None
    ai_reason: Optional[str] = None
    ai_confidence: Optional[float] = None
    final_decision: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    patient: Optional[PatientRead] = None
    protocol: Optional[MedicationProtocolRead] = None

    class Config:
        from_attributes = True


class RefillRequestCreate(BaseModel):
    """Schema for creating a refill request."""
    patient_id: int
    protocol_id: int


class ReviewPayload(BaseModel):
    """Payload for reviewing a refill request."""
    decision: str = Field(..., description="'Approve' or 'Deny'")
    user_id: str = Field(..., description="Clinical staff member ID")


class RefillDetailData(BaseModel):
    """Comprehensive data for a refill request detail page."""
    request: RefillRequestRead
    patient_data: dict = Field(..., description="EMR patient data")
    clinical_data: dict = Field(..., description="EMR clinical data (visits, labs, etc.)")
    protocols_checked: list[dict] = Field(
        ...,
        description="List of protocol checks with status and EMR data"
    )

