# Entity-Relationship (ER) Diagram

This diagram outlines the schema of our PostgreSQL database.

```mermaid
erDiagram
    PATIENT ||--o{ REFILL_REQUEST : "has"
    MEDICATION_PROTOCOL ||--o{ REFILL_REQUEST : "applies to"

    PATIENT {
        int id PK
        varchar mrn UK "Medical Record Number"
        varchar first_name
        varchar last_name
        date date_of_birth
    }

    MEDICATION_PROTOCOL {
        int id PK
        varchar medication_class UK
        int max_months_since_visit
        float max_a1c_value
        int require_recent_a1c "in months"
    }

    REFILL_REQUEST {
        int id PK
        int patient_id FK
        int protocol_id FK
        varchar status "e.g., PENDING_AI_REVIEW"
        varchar ai_decision "Approve/Deny"
        text ai_reason
        float ai_confidence
        varchar final_decision "Approve/Deny"
        datetime created_at
    }
```

### Entities

*   **PATIENT**: Stores information about the patients.
    *   `mrn` is a unique key to identify patients.
*   **MEDICATION_PROTOCOL**: Defines the rules for different classes of medications.
    *   `medication_class` is a unique key.
*   **REFILL_REQUEST**: The central table that links patients to medication protocols for a specific refill request.
    *   It contains foreign keys (`FK`) to the `PATIENT` and `MEDICATION_PROTOCOL` tables.
    *   It stores the state of the request, the AI's analysis, and the final human decision.
