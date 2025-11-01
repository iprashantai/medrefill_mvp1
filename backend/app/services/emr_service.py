"""
Mock EMR service for patient and clinical data.
In production, this would connect to a real EMR system.
"""
from typing import Dict
from datetime import date, datetime, timedelta


def get_patient_data(mrn: str) -> Dict:
    """
    Mock function to retrieve patient demographics.
    Enterprise-grade mock data for Fortune 50 healthcare company demos.
    
    Args:
        mrn: Medical Record Number
        
    Returns:
        Dictionary with patient information
    """
    # Enterprise mock patients for realistic demo
    patients = {
        "12345": {"first_name": "John", "last_name": "Doe", "dob": "1975-04-10"},
        "67890": {"first_name": "Jane", "last_name": "Smith", "dob": "1980-06-15"},
        "23456": {"first_name": "Michael", "last_name": "Martin", "dob": "1968-03-22"},
        "34567": {"first_name": "Sarah", "last_name": "Johnson", "dob": "1972-11-08"},
        "45678": {"first_name": "Robert", "last_name": "Williams", "dob": "1985-07-14"},
        "56789": {"first_name": "Emily", "last_name": "Davis", "dob": "1979-09-30"},
        "78901": {"first_name": "David", "last_name": "Brown", "dob": "1965-12-05"},
        "89012": {"first_name": "Lisa", "last_name": "Anderson", "dob": "1983-02-18"},
        "90123": {"first_name": "James", "last_name": "Wilson", "dob": "1977-08-25"},
        "01234": {"first_name": "Patricia", "last_name": "Taylor", "dob": "1971-05-11"},
    }
    
    patient = patients.get(mrn)
    if patient:
        return {
            "mrn": mrn,
            "first_name": patient["first_name"],
            "last_name": patient["last_name"],
            "dob": patient["dob"]
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
    
    # Additional enterprise mock clinical scenarios
    clinical_scenarios = {
        "23456": {  # Michael Martin - Edge case
            "last_visit_date": (today - timedelta(days=395)).strftime("%Y-%m-%d"),  # 13 months
            "labs": {
                "A1c": {
                    "value": 7.9,
                    "date": (today - timedelta(days=120)).strftime("%Y-%m-%d")
                }
            }
        },
        "34567": {  # Sarah Johnson - Approve
            "last_visit_date": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 6.2,
                    "date": (today - timedelta(days=20)).strftime("%Y-%m-%d")
                }
            }
        },
        "45678": {  # Robert Williams - Deny (A1c too high)
            "last_visit_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 8.5,
                    "date": (today - timedelta(days=45)).strftime("%Y-%m-%d")
                }
            }
        },
        "56789": {  # Emily Davis - Approve
            "last_visit_date": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 6.8,
                    "date": (today - timedelta(days=15)).strftime("%Y-%m-%d")
                }
            }
        },
        "78901": {  # David Brown - Deny (old visit + old labs)
            "last_visit_date": (today - timedelta(days=420)).strftime("%Y-%m-%d"),  # 14 months
            "labs": {
                "A1c": {
                    "value": 7.5,
                    "date": (today - timedelta(days=210)).strftime("%Y-%m-%d")  # 7 months old
                }
            }
        },
        "89012": {  # Lisa Anderson - Approve
            "last_visit_date": (today - timedelta(days=75)).strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 6.9,
                    "date": (today - timedelta(days=60)).strftime("%Y-%m-%d")
                }
            }
        },
        "90123": {  # James Wilson - Approve
            "last_visit_date": (today - timedelta(days=50)).strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 7.1,
                    "date": (today - timedelta(days=40)).strftime("%Y-%m-%d")
                }
            }
        },
        "01234": {  # Patricia Taylor - Deny (visit OK but A1c too high)
            "last_visit_date": (today - timedelta(days=100)).strftime("%Y-%m-%d"),
            "labs": {
                "A1c": {
                    "value": 8.2,
                    "date": (today - timedelta(days=50)).strftime("%Y-%m-%d")
                }
            }
        },
    }
    
    if mrn in clinical_scenarios:
        return clinical_scenarios[mrn]
    
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

