"""
Mock EMR service for patient and clinical data.
In production, this would connect to a real EMR system.
"""
from typing import Dict
from datetime import date, datetime, timedelta


def get_patient_data(mrn: str) -> Dict:
    """
    Mock function to retrieve patient demographics.
    
    Args:
        mrn: Medical Record Number
        
    Returns:
        Dictionary with patient information
    """
    # Mock patient data - "Deny" case
    if mrn == "12345":
        return {
            "mrn": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "1975-04-10"
        }
    
    # Mock patient data - "Approve" case
    elif mrn == "67890":
        return {
            "mrn": "67890",
            "first_name": "Jane",
            "last_name": "Smith",
            "dob": "1980-06-15"
        }
    
    # Default mock patient
    return {
        "mrn": mrn,
        "first_name": "Patient",
        "last_name": "Unknown",
        "dob": "1970-01-01"
    }


def get_patient_clinical_data(mrn: str) -> Dict:
    """
    Mock function to retrieve patient clinical data (visits, labs, etc.).
    
    This returns different data based on MRN to simulate different scenarios:
    - MRN "12345": Returns data that violates protocols (DENY case)
    - MRN "67890": Returns data that passes protocols (APPROVE case)
    
    Args:
        mrn: Medical Record Number
        
    Returns:
        Dictionary with clinical data including:
        - last_visit_date: Last visit date (string YYYY-MM-DD)
        - labs: Dictionary of lab results with values and dates
    """
    today = date.today()
    
    # Mock clinical data for "Deny" case (MRN 12345)
    if mrn == "12345":
        # Last visit was more than 12 months ago
        last_visit = today - timedelta(days=575)  # ~18.85 months
        return {
            "last_visit_date": last_visit.strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 7.8,
                    "date": (today - timedelta(days=30)).strftime("%Y-%m-%d")
                }
            }
        }
    
    # Mock clinical data for "Approve" case (MRN 67890)
    elif mrn == "67890":
        # Recent visit and good A1c
        last_visit = today - timedelta(days=60)  # ~2 months ago
        return {
            "last_visit_date": last_visit.strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 6.5,
                    "date": (today - timedelta(days=30)).strftime("%Y-%m-%d")
                }
            }
        }
    
    # Default mock clinical data
    return {
        "last_visit_date": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
        "labs": {
            "A1c": {
                "value": 7.0,
                "date": (today - timedelta(days=90)).strftime("%Y-%m-%d")
            }
        }
    }

