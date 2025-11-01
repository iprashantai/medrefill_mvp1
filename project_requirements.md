# **IgniteHealth MedRefills \- MVP Requirements**

This document outlines the functional and non-functional requirements for the MedRefills AI MVP.

## **1\. Actors**

* **Clinician:** A qualified staff member (LVN, MA, NP) responsible for final review.  
* **System:** The automated MedRefills platform.  
* **AI Agent (Sub-system):** The LangChain-based multi-agent system (Primary, QA, Manager).

## **2\. Functional Requirements (User Stories)**

### **Epic: Automated Refill Processing**

**User Story 1: System Batch Identification**

* **As a** System  
* **I want** to run a daily batch job  
* **So that** I can identify all active patients who have medications due for a refill in the next 14 days.

**User Story 2: AI Protocol Review**

* **As an** AI Agent  
* **I want** to receive a patient and their medication list  
* **So that** I can:  
  1. Fetch the required protocols for each medication.  
  2. Fetch the required EMR data (last visit, labs like A1c) for those protocols.  
  3. Compare the EMR data against the protocol rules.  
  4. Generate an "Approve" or "Deny" recommendation with a clear reason.

**User Story 3: Multi-Agent QA**

* **As a** System  
* **I want** a Primary AI Agent to conduct the review and a QA AI Agent to validate the review  
* **So that** I can ensure high accuracy and flag any discrepancies for a Manager Agent or human escalated review.

### **Epic: Human-in-the-Loop (HITL) Review**

**User Story 4: Clinician Review Queue**

* **As a** Clinician  
* **I want** to see a dashboard queue of all refill requests that require my review  
* **So that** I can efficiently process them.  
* **Acceptance Criteria:**  
  * The queue is sorted to show "AI Deny" recommendations first.  
  * Each item shows the Patient Name, Medication, and AI Recommendation.

**User Story 5: Clinician Detail View**

* **As a** Clinician  
* **I want** to click on a request and see all relevant information in one place  
* **So that** I can make a final decision in under 30 seconds.  
* **Acceptance Criteria:**  
  * The view MUST display (similar to PDF Page 4):  
    * Patient Demographics (Name, DOB, MRN).  
    * Medication to be refilled.  
    * AI Recommendation (e.g., 90% Deny) and the specific reason.  
    * The list of protocols that were checked.  
    * The supporting EMR data (e.g., "Last Visit Date: 2024-03-26", "Protocol requires \< 12 months").

**User Story 6: Clinician Final Action**

* **As a** Clinician  
* **I want** to have "Approve Refill" and "Deny Refill" buttons  
* **So that** I can finalize the request.  
* **Acceptance Criteria:**  
  * Clicking "Approve" updates the request status and (in future) triggers the e-script.  
  * Clicking "Deny" updates the request status and (in future) generates a task to contact the patient.  
  * All actions are logged in an audit trail.

## **3\. Non-Functional Requirements**

1. **Security:** All operations must be HIPAA compliant. Data at rest and in transit must be encrypted.  
2. **EMR Integration:** The system must interface with the eClinicalWorks (eCW) API. All data pulls must be efficient and targeted to avoid rate-limiting.  
3. **Auditability:** Every single action (AI decision, human click) must be logged for compliance and review.  
4. **Performance:** The HITL detail view must load in \< 3 seconds. The AI review for a single patient should take \< 60 seconds.