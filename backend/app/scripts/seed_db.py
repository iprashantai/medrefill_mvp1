"""
Enterprise seed script to populate the database with comprehensive demo data.
Creates realistic data for Fortune 50 healthcare company demonstrations.
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
    """Seed the database with comprehensive enterprise demo data."""
    print("🚀 Initializing database and creating tables...")
    create_db_and_tables()
    
    with Session(engine) as session:
        # Define enterprise patients
        patients_data = [
            {"mrn": "12345", "first_name": "John", "last_name": "Doe", "dob": date(1975, 4, 10)},
            {"mrn": "67890", "first_name": "Jane", "last_name": "Smith", "dob": date(1980, 6, 15)},
            {"mrn": "23456", "first_name": "Michael", "last_name": "Martin", "dob": date(1968, 3, 22)},
            {"mrn": "34567", "first_name": "Sarah", "last_name": "Johnson", "dob": date(1972, 11, 8)},
            {"mrn": "45678", "first_name": "Robert", "last_name": "Williams", "dob": date(1985, 7, 14)},
            {"mrn": "56789", "first_name": "Emily", "last_name": "Davis", "dob": date(1979, 9, 30)},
            {"mrn": "78901", "first_name": "David", "last_name": "Brown", "dob": date(1965, 12, 5)},
            {"mrn": "89012", "first_name": "Lisa", "last_name": "Anderson", "dob": date(1983, 2, 18)},
        ]
        
        # Create or get patients
        patients = []
        for p_data in patients_data:
            statement = select(Patient).where(Patient.mrn == p_data["mrn"])
            patient = session.exec(statement).first()
            if not patient:
                patient = Patient(**p_data)
                session.add(patient)
                session.commit()
            session.refresh(patient)
            patients.append(patient)
            print(f"   ✓ Patient: {patient.first_name} {patient.last_name} (MRN: {patient.mrn})")
        
        # Define medication protocols
        protocols_data = [
            {
                "medication_class": "SGLT2 Inhibitor",
                "max_months_since_visit": 12,
                "max_a1c_value": 8.0,
                "require_recent_a1c": 6
            },
            {
                "medication_class": "GLP-1 Agonist",
                "max_months_since_visit": 12,
                "max_a1c_value": 8.0,
                "require_recent_a1c": 6
            },
            {
                "medication_class": "Antihypertensive (ACE/ARB)",
                "max_months_since_visit": 12,
                "max_a1c_value": None,
                "require_recent_a1c": None
            },
            {
                "medication_class": "Antilipemic (Statin)",
                "max_months_since_visit": 12,
                "max_a1c_value": None,
                "require_recent_a1c": None
            },
        ]
        
        # Create or get protocols
        protocols = []
        for prot_data in protocols_data:
            statement = select(MedicationProtocol).where(
                MedicationProtocol.medication_class == prot_data["medication_class"]
            )
            protocol = session.exec(statement).first()
            if not protocol:
                protocol = MedicationProtocol(**prot_data)
                session.add(protocol)
                session.commit()
            session.refresh(protocol)
            protocols.append(protocol)
            print(f"   ✓ Protocol: {protocol.medication_class}")
        
        # Create refill requests with varied scenarios
        print("\n📋 Creating refill requests and running AI reviews...")
        
        # Request scenarios: (patient_idx, protocol_idx, expected_outcome)
        request_scenarios = [
            (0, 0, "Deny"),      # John Doe - SGLT2 - Deny (old visit)
            (1, 1, "Approve"),   # Jane Smith - GLP-1 - Approve
            (2, 0, "Deny"),      # Michael Martin - SGLT2 - Deny (edge case)
            (3, 1, "Approve"),   # Sarah Johnson - GLP-1 - Approve
            (4, 0, "Deny"),      # Robert Williams - SGLT2 - Deny (high A1c)
            (5, 1, "Approve"),   # Emily Davis - GLP-1 - Approve
            (6, 0, "Deny"),      # David Brown - SGLT2 - Deny (old everything)
            (7, 1, "Approve"),   # Lisa Anderson - GLP-1 - Approve
            (1, 2, "Approve"),   # Jane Smith - Antihypertensive - Approve
            (3, 3, "Approve"),   # Sarah Johnson - Statin - Approve
        ]
        
        created_requests = []
        
        for idx, (patient_idx, protocol_idx, expected) in enumerate(request_scenarios, 1):
            patient = patients[patient_idx]
            protocol = protocols[protocol_idx]
            
            # Check if request already exists
            statement = select(RefillRequest).where(
                RefillRequest.patient_id == patient.id,
                RefillRequest.protocol_id == protocol.id
            )
            existing = session.exec(statement).first()
            
            if existing:
                print(f"   ⏭️  Request {idx}: Already exists for {patient.first_name} {patient.last_name} - {protocol.medication_class}")
                created_requests.append(existing)
                continue
            
            # Create new request
            request = RefillRequest(
                patient_id=patient.id,
                protocol_id=protocol.id,
                status=RefillStatus.PENDING_AI_REVIEW
            )
            session.add(request)
            session.commit()
            session.refresh(request)
            
            # Run AI review
            print(f"   🔄 Request {idx}/{len(request_scenarios)}: Running AI review for {patient.first_name} {patient.last_name} - {protocol.medication_class}...")
            try:
                ai_result = run_ai_review(patient.mrn, protocol.medication_class)
                request.ai_decision = ai_result["decision"]
                request.ai_reason = ai_result["reason"]
                request.ai_confidence = ai_result["confidence"]
                request.status = RefillStatus.PENDING_HUMAN_REVIEW
                session.add(request)
                
                # Show result
                status_icon = "✓" if ai_result["decision"] == expected else "⚠️"
                print(f"      {status_icon} AI Decision: {ai_result['decision']} (Confidence: {ai_result['confidence']:.0f}%)")
                
            except Exception as e:
                print(f"      ❌ Error in AI review: {str(e)}")
                # Set default values even if AI fails
                request.ai_decision = "Deny"
                request.ai_reason = f"Error during AI review: {str(e)}"
                request.ai_confidence = 0
                request.status = RefillStatus.PENDING_HUMAN_REVIEW
                session.add(request)
            
            created_requests.append(request)
        
        session.commit()
        
        # Print summary
        print("\n" + "="*60)
        print("✅ Database seeded successfully!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Patients: {len(patients)}")
        print(f"   • Medication Protocols: {len(protocols)}")
        print(f"   • Refill Requests: {len(created_requests)}")
        
        # Breakdown by decision
        approve_count = sum(1 for r in created_requests if r.ai_decision == "Approve")
        deny_count = sum(1 for r in created_requests if r.ai_decision == "Deny")
        print(f"\n🤖 AI Decisions:")
        print(f"   • Approved: {approve_count}")
        print(f"   • Denied: {deny_count}")
        print(f"\n📝 Request IDs: {', '.join(str(r.id) for r in created_requests)}")
        print("\n💡 All requests are ready for human review in the dashboard!")
        print("="*60)


if __name__ == "__main__":
    seed_database()
