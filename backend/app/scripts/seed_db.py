"""
Script to seed the database with sample data for testing.
Run this after the database is created.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select
from app.core.db import engine, create_db_and_tables
from app.models import Patient, MedicationProtocol, RefillRequest, RefillStatus
from app.agents.medrefill_agents import run_ai_review
from datetime import date, datetime


def seed_database():
    """Seed the database with sample data."""
    # Create tables
    create_db_and_tables()
    
    with Session(engine) as session:
        from sqlmodel import select
        
        # Check if patients already exist, or create them
        statement = select(Patient).where(Patient.mrn == "12345")
        patient1 = session.exec(statement).first()
        if not patient1:
            patient1 = Patient(
                mrn="12345",
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1975, 4, 10)
            )
            session.add(patient1)
            session.commit()
        session.refresh(patient1)
        
        statement = select(Patient).where(Patient.mrn == "67890")
        patient2 = session.exec(statement).first()
        if not patient2:
            patient2 = Patient(
                mrn="67890",
                first_name="Jane",
                last_name="Smith",
                date_of_birth=date(1980, 6, 15)
            )
            session.add(patient2)
            session.commit()
        session.refresh(patient2)
        
        # Check if protocols already exist, or create them
        statement = select(MedicationProtocol).where(MedicationProtocol.medication_class == "SGLT2 Inhibitor")
        protocol1 = session.exec(statement).first()
        if not protocol1:
            protocol1 = MedicationProtocol(
                medication_class="SGLT2 Inhibitor",
                max_months_since_visit=12,
                max_a1c_value=8.0,
                require_recent_a1c=6
            )
            session.add(protocol1)
            session.commit()
        session.refresh(protocol1)
        
        statement = select(MedicationProtocol).where(MedicationProtocol.medication_class == "GLP-1 Agonist")
        protocol2 = session.exec(statement).first()
        if not protocol2:
            protocol2 = MedicationProtocol(
                medication_class="GLP-1 Agonist",
                max_months_since_visit=12,
                max_a1c_value=8.0,
                require_recent_a1c=6
            )
            session.add(protocol2)
            session.commit()
        session.refresh(protocol2)
        
        # Create refill requests and run AI review
        print("Creating refill requests and running AI reviews...")
        
        # Request 1: Patient 1 (Deny case)
        request1 = RefillRequest(
            patient_id=patient1.id,
            protocol_id=protocol1.id,
            status=RefillStatus.PENDING_AI_REVIEW
        )
        session.add(request1)
        session.commit()
        session.refresh(request1)
        
        # Run AI review
        print(f"Running AI review for request {request1.id}...")
        ai_result = run_ai_review(patient1.mrn, protocol1.medication_class)
        request1.ai_decision = ai_result["decision"]
        request1.ai_reason = ai_result["reason"]
        request1.ai_confidence = ai_result["confidence"]
        request1.status = RefillStatus.PENDING_HUMAN_REVIEW
        session.add(request1)
        
        # Request 2: Patient 2 (Approve case)
        request2 = RefillRequest(
            patient_id=patient2.id,
            protocol_id=protocol2.id,
            status=RefillStatus.PENDING_AI_REVIEW
        )
        session.add(request2)
        session.commit()
        session.refresh(request2)
        
        # Run AI review
        print(f"Running AI review for request {request2.id}...")
        ai_result = run_ai_review(patient2.mrn, protocol2.medication_class)
        request2.ai_decision = ai_result["decision"]
        request2.ai_reason = ai_result["reason"]
        request2.ai_confidence = ai_result["confidence"]
        request2.status = RefillStatus.PENDING_HUMAN_REVIEW
        session.add(request2)
        
        session.commit()
        
        print("\n✅ Database seeded successfully!")
        print(f"   - Created 2 patients (MRN: 12345, 67890)")
        print(f"   - Created 2 medication protocols")
        print(f"   - Created 2 refill requests (both pending human review)")
        print(f"\n   Request IDs: {request1.id}, {request2.id}")


if __name__ == "__main__":
    seed_database()

