"""
API endpoints for refill requests.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from app.core.db import get_session
from app.models import RefillRequest, Patient, MedicationProtocol, RefillStatus
from app.schemas import RefillRequestRead, ReviewPayload, RefillDetailData
from app.services.emr_service import get_patient_data, get_patient_clinical_data

router = APIRouter(prefix="/api/v1", tags=["refill-requests"])


@router.get("/refill-queue", response_model=List[RefillRequestRead])
def get_refill_queue(session: Session = Depends(get_session)):
    """
    Fetch all refill requests pending human review.
    Sorts to show "Deny" recommendations first.
    """
    # Get all pending human review requests
    statement = select(RefillRequest).where(
        RefillRequest.status == RefillStatus.PENDING_HUMAN_REVIEW
    )
    requests = list(session.exec(statement).all())
    
    # Sort: Deny first, then Approve
    requests.sort(key=lambda r: (r.ai_decision != "Deny", r.created_at))
    
    # Load relationships
    for req in requests:
        req.patient = session.get(Patient, req.patient_id)
        req.protocol = session.get(MedicationProtocol, req.protocol_id)
    
    return requests


@router.get("/refill-request/{request_id}", response_model=RefillDetailData)
def get_refill_detail(request_id: int, session: Session = Depends(get_session)):
    """
    Fetch a single refill request with all supporting data.
    
    This endpoint:
    1. Fetches the RefillRequest from DB
    2. Fetches patient and protocol data
    3. Calls mock EMR service to get clinical data
    4. Returns comprehensive detail data
    """
    # Get the request
    request = session.get(RefillRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Refill request not found")
    
    # Load relationships
    patient = session.get(Patient, request.patient_id)
    protocol = session.get(MedicationProtocol, request.protocol_id)
    
    if not patient or not protocol:
        raise HTTPException(status_code=404, detail="Related data not found")
    
    # Get EMR data
    patient_data = get_patient_data(patient.mrn)
    clinical_data = get_patient_clinical_data(patient.mrn)
    
    # Build protocols_checked list
    protocols_checked = []
    
    # Check last visit
    if protocol.max_months_since_visit is not None:
        last_visit_str = clinical_data.get("last_visit_date")
        if last_visit_str:
            from datetime import date
            last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d").date()
            today = date.today()
            months_since_visit = (today - last_visit).days / 30.4
            
            status = "✅ PASS" if months_since_visit <= protocol.max_months_since_visit else "❌ FAILED"
            protocols_checked.append({
                "protocol": f"Last Visit < {protocol.max_months_since_visit}mo",
                "emr_data": f"{months_since_visit:.1f} months",
                "status": status
            })
    
    # Check A1c value
    if protocol.max_a1c_value is not None:
        labs = clinical_data.get("labs", {})
        a1c = labs.get("A1c", {})
        a1c_value = a1c.get("value")
        
        if a1c_value is not None:
            status = "✅ PASS" if a1c_value <= protocol.max_a1c_value else "❌ FAILED"
            protocols_checked.append({
                "protocol": f"A1c < {protocol.max_a1c_value}",
                "emr_data": str(a1c_value),
                "status": status
            })
        else:
            protocols_checked.append({
                "protocol": f"A1c < {protocol.max_a1c_value}",
                "emr_data": "No A1c data",
                "status": "❌ FAILED"
            })
    
    # Check recent A1c requirement
    if protocol.require_recent_a1c is not None:
        labs = clinical_data.get("labs", {})
        a1c = labs.get("A1c", {})
        a1c_date_str = a1c.get("date")
        
        if a1c_date_str:
            from datetime import date
            a1c_date = datetime.strptime(a1c_date_str, "%Y-%m-%d").date()
            today = date.today()
            months_since_a1c = (today - a1c_date).days / 30.4
            
            status = "✅ PASS" if months_since_a1c <= protocol.require_recent_a1c else "❌ FAILED"
            protocols_checked.append({
                "protocol": f"A1c within {protocol.require_recent_a1c}mo",
                "emr_data": f"{months_since_a1c:.1f} months ago",
                "status": status
            })
        else:
            protocols_checked.append({
                "protocol": f"A1c within {protocol.require_recent_a1c}mo",
                "emr_data": "No A1c date",
                "status": "❌ FAILED"
            })
    
    # Create request read schema
    request_read = RefillRequestRead(
        id=request.id,
        patient_id=request.patient_id,
        protocol_id=request.protocol_id,
        status=request.status.value,
        ai_decision=request.ai_decision,
        ai_reason=request.ai_reason,
        ai_confidence=request.ai_confidence,
        final_decision=request.final_decision,
        reviewed_by=request.reviewed_by,
        reviewed_at=request.reviewed_at,
        created_at=request.created_at,
        updated_at=request.updated_at,
        patient=patient,
        protocol=protocol
    )
    
    return RefillDetailData(
        request=request_read,
        patient_data=patient_data,
        clinical_data=clinical_data,
        protocols_checked=protocols_checked
    )


@router.post("/refill-request/{request_id}/review", response_model=RefillRequestRead)
def review_refill_request(
    request_id: int,
    payload: ReviewPayload,
    session: Session = Depends(get_session)
):
    """
    Submit a human review decision for a refill request.
    
    Updates the RefillRequest with:
    - final_decision: "Approve" or "Deny"
    - reviewed_by: User ID
    - reviewed_at: Current timestamp
    - status: Updated based on decision
    """
    # Get the request
    request = session.get(RefillRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Refill request not found")
    
    # Validate decision
    if payload.decision not in ["Approve", "Deny"]:
        raise HTTPException(
            status_code=400,
            detail="decision must be either 'Approve' or 'Deny'"
        )
    
    # Update the request
    request.final_decision = payload.decision
    request.reviewed_by = payload.user_id
    request.reviewed_at = datetime.utcnow()
    
    # Update status based on decision
    if payload.decision == "Approve":
        request.status = RefillStatus.APPROVED
    else:
        request.status = RefillStatus.DENIED
    
    request.updated_at = datetime.utcnow()
    
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Load relationships for response
    request.patient = session.get(Patient, request.patient_id)
    request.protocol = session.get(MedicationProtocol, request.protocol_id)
    
    return request

