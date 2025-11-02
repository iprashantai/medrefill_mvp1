# Use Case Diagram

This diagram shows the key interactions between our users (actors) and the MedRefills AI system.

```mermaid
graph TD
    Clinician[Clinician]
    subgraph MedRefills_AI_System
        UC1["View Refill Queue"]
        UC2["Filter and Sort Queue"]
        UC3["View Request Details"]
        UC4["Review AI Analysis"]
        UC5["Approve Refill"]
        UC6["Deny Refill"]
    end

    Clinician -- "Logs in to" --> UC1
    Clinician -- "Manages workflow with" --> UC2
    Clinician -- "Selects request to" --> UC3
    UC3 -- "Includes" --> UC4
    Clinician -- "Makes final decision to" --> UC5
    Clinician -- "Makes final decision to" --> UC6

```

### Actors

- **Clinician**: A licensed healthcare professional (e.g., nurse, pharmacist, doctor) responsible for reviewing and actioning medication refill requests.

### Use Cases

- **View Refill Queue**: The clinician sees a list of all pending refill requests.
- **Filter and Sort Queue**: The clinician can organize the queue by various criteria like AI decision, patient name, or medication.
- **View Request Details**: The clinician selects a specific request to see all relevant information, including patient data and AI analysis.
- **Review AI Analysis**: As part of viewing details, the clinician examines the AI's recommendation, confidence score, and reasoning.
- **Approve Refill**: The clinician agrees with the refill request and approves it.
- **Deny Refill**: The clinician disagrees with the refill request and denies it.
