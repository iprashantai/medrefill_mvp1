"""
LangChain tools for the MedRefills AI agent.
This includes the ProtocolCheckTool which acts as the "Rules Engine".
"""
from typing import Optional
from datetime import date, datetime
from langchain.tools import BaseTool
from pydantic import Field
from sqlmodel import Session, select

from app.models import MedicationProtocol
from app.services.emr_service import get_patient_clinical_data


class ProtocolCheckTool(BaseTool):
    """
    Custom LangChain tool that checks medication protocols against patient EMR data.
    
    This tool:
    1. Fetches patient clinical data from the EMR service
    2. Retrieves protocol rules for the medication class from the database
    3. Evaluates each rule against the EMR data
    4. Returns a JSON decision string with reason
    """
    name = "protocol_check"
    description = """
    Checks if a patient meets medication refill protocols.
    
    Input should be a JSON string with:
    - patient_mrn: The patient's Medical Record Number
    - medication_class: The class of medication (e.g., 'SGLT2 Inhibitor', 'GLP-1 Agonist')
    
    Returns a JSON string with:
    - decision: 'Approve' or 'Deny'
    - reason: Explanation of the decision
    """
    
    # We'll pass the database session via the tool initialization
    session: Optional[Session] = Field(default=None, exclude=True)
    
    def _run(self, input_str: str) -> str:
        """
        Execute the protocol check tool.
        
        Args:
            input_str: JSON string with patient_mrn and medication_class
            
        Returns:
            JSON string with decision and reason
        """
        import json
        
        try:
            # Parse input
            input_data = json.loads(input_str)
            patient_mrn = input_data.get("patient_mrn")
            medication_class = input_data.get("medication_class")
            
            if not patient_mrn or not medication_class:
                return json.dumps({
                    "decision": "Deny",
                    "reason": "Missing required fields: patient_mrn or medication_class"
                })
            
            # Get EMR clinical data
            emr_data = get_patient_clinical_data(patient_mrn)
            
            # Get protocol from database
            # Use the session if provided, otherwise create a new one
            if self.session:
                session = self.session
                close_session = False
            else:
                from app.core.db import engine
                session = Session(engine)
                close_session = True
            
            try:
                statement = select(MedicationProtocol).where(
                    MedicationProtocol.medication_class == medication_class
                )
                protocol = session.exec(statement).first()
                
                if not protocol:
                    return json.dumps({
                        "decision": "Deny",
                        "reason": f"No protocol found for medication class: {medication_class}"
                    })
                
                # Parse last visit date from EMR data
                last_visit_date_str = emr_data.get("last_visit_date")
                if last_visit_date_str:
                    last_visit_date = datetime.strptime(last_visit_date_str, "%Y-%m-%d").date()
                    today = date.today()
                    months_since_visit = (today - last_visit_date).days / 30.4
                else:
                    months_since_visit = None
                
                # Check protocol rules
                violations = []
                
                # Rule 1: Check max_months_since_visit
                if protocol.max_months_since_visit is not None and months_since_visit is not None:
                    if months_since_visit > protocol.max_months_since_visit:
                        violations.append(
                            f"Patient last visit was {months_since_visit:.1f} months ago. "
                            f"Protocol violation (max {protocol.max_months_since_visit})."
                        )
                
                # Rule 2: Check max_a1c_value
                if protocol.max_a1c_value is not None:
                    labs = emr_data.get("labs", {})
                    a1c = labs.get("A1c", {})
                    a1c_value = a1c.get("value")
                    
                    if a1c_value is not None and a1c_value > protocol.max_a1c_value:
                        violations.append(
                            f"Patient A1c ({a1c_value}) exceeds protocol maximum ({protocol.max_a1c_value})."
                        )
                
                # Rule 3: Check require_recent_a1c
                if protocol.require_recent_a1c is not None:
                    labs = emr_data.get("labs", {})
                    a1c = labs.get("A1c", {})
                    a1c_date_str = a1c.get("date")
                    
                    if a1c_date_str:
                        a1c_date = datetime.strptime(a1c_date_str, "%Y-%m-%d").date()
                        today = date.today()
                        months_since_a1c = (today - a1c_date).days / 30.4
                        
                        if months_since_a1c > protocol.require_recent_a1c:
                            violations.append(
                                f"Patient A1c is {months_since_a1c:.1f} months old. "
                                f"Protocol requires A1c within {protocol.require_recent_a1c} months."
                            )
                    else:
                        violations.append("No A1c lab result found. Protocol requires recent A1c.")
                
                # Make decision
                if violations:
                    reason = " | ".join(violations)
                    decision = "Deny"
                else:
                    decision = "Approve"
                    reason = "All protocols passed."
                
                return json.dumps({
                    "decision": decision,
                    "reason": reason
                })
                
            finally:
                if close_session:
                    session.close()
                    
        except Exception as e:
            return json.dumps({
                "decision": "Deny",
                "reason": f"Error checking protocols: {str(e)}"
            })
    
    async def _arun(self, input_str: str) -> str:
        """Async version of _run (not implemented for MVP)."""
        return self._run(input_str)

