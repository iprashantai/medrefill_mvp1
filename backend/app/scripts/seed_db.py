"""
Enterprise seed script to populate the database with a large, realistic dataset.
"""
import sys
import random
from pathlib import Path
from faker import Faker
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import Session, select
from app.core.db import engine, create_db_and_tables
from app.models import Patient, MedicationProtocol, RefillRequest, RefillStatus
from app.agents.medrefill_agents import run_ai_review

# --- CONFIGURATION ---
NUM_PATIENTS = 100
NUM_REFILL_REQUESTS = 250
# ---------------------

fake = Faker()

def seed_database():
    """Seed the database with a large and varied dataset."""
    print("🚀 Initializing database and creating tables...")
    create_db_and_tables()
    
    with Session(engine) as session:
        # --- 1. Clear Existing Data ---
        print("🗑️ Clearing existing refill requests...")
        session.query(RefillRequest).delete()
        session.query(Patient).delete()
        session.query(MedicationProtocol).delete()
        session.commit()

        # --- 2. Create Medication Protocols ---
        print("💊 Creating medication protocols...")
        protocols_data = [
            {"medication_class": "SGLT2 Inhibitor", "max_months_since_visit": 12, "max_a1c_value": 8.0, "require_recent_a1c": 6},
            {"medication_class": "GLP-1 Agonist", "max_months_since_visit": 12, "max_a1c_value": 8.0, "require_recent_a1c": 6},
            {"medication_class": "Antihypertensive (ACE/ARB)", "max_months_since_visit": 12, "max_a1c_value": None, "require_recent_a1c": None},
            {"medication_class": "Antilipemic (Statin)", "max_months_since_visit": 12, "max_a1c_value": None, "require_recent_a1c": None},
            {"medication_class": "Beta-Blocker", "max_months_since_visit": 18, "max_a1c_value": None, "require_recent_a1c": None},
            {"medication_class": "Thyroid Hormone", "max_months_since_visit": 18, "max_a1c_value": None, "require_recent_a1c": None},
        ]
        protocols = [MedicationProtocol(**p) for p in protocols_data]
        session.add_all(protocols)
        session.commit()
        for p in protocols:
            session.refresh(p)
        print(f"   ✓ Created {len(protocols)} protocols.")

        # --- 3. Create Patients ---
        print(f"👥 Creating {NUM_PATIENTS} patients...")
        patients = []
        for i in range(NUM_PATIENTS):
            first_name = fake.first_name()
            last_name = fake.last_name()
            patient = Patient(
                mrn=f"{random.randint(10000, 99999)}-{i}",
                first_name=first_name,
                last_name=last_name,
                date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=85)
            )
            patients.append(patient)
        session.add_all(patients)
        session.commit()
        for p in patients:
            session.refresh(p)
        print(f"   ✓ Created {len(patients)} patients.")

        # --- 4. Create Refill Requests & Run AI Review ---
        print(f"📋 Creating {NUM_REFILL_REQUESTS} refill requests and running AI reviews...")
        created_requests = []
        for i in range(NUM_REFILL_REQUESTS):
            patient = random.choice(patients)
            protocol = random.choice(protocols)
            
            request = RefillRequest(
                patient_id=patient.id,
                protocol_id=protocol.id,
                status=RefillStatus.PENDING_AI_REVIEW
            )
            session.add(request)
            session.commit()
            session.refresh(request)
            
            print(f"   🔄 Request {i+1}/{NUM_REFILL_REQUESTS}: AI review for {patient.first_name} - {protocol.medication_class}...")
            try:
                ai_result = run_ai_review(patient.mrn, protocol.medication_class)
                request.ai_decision = ai_result["decision"]
                request.ai_reason = ai_result["reason"]
                request.ai_confidence = ai_result["confidence"]
                request.status = RefillStatus.PENDING_HUMAN_REVIEW
                session.add(request)
                print(f"      ✓ AI Decision: {ai_result['decision']} ({ai_result['confidence']:.0f}%)")
            except Exception as e:
                print(f"      ❌ Error in AI review: {str(e)}")
                request.ai_decision = "Deny"
                request.ai_reason = f"Error during AI review: {str(e)}"
                request.ai_confidence = 0
                request.status = RefillStatus.PENDING_HUMAN_REVIEW
                session.add(request)
            
            created_requests.append(request)
            session.commit()

        # --- 5. Final Summary ---
        print("\n" + "="*60)
        print("✅ Database seeded successfully!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Patients: {len(patients)}")
        print(f"   • Medication Protocols: {len(protocols)}")
        print(f"   • Refill Requests: {len(created_requests)}")
        
        approve_count = sum(1 for r in created_requests if r.ai_decision == "Approve")
        deny_count = sum(1 for r in created_requests if r.ai_decision == "Deny")
        print(f"\n🤖 AI Decisions:")
        print(f"   • Approved: {approve_count}")
        print(f"   • Denied: {deny_count}")
        print("\n💡 All requests are ready for human review in the dashboard!")
        print("="*60)

if __name__ == "__main__":
    seed_database()