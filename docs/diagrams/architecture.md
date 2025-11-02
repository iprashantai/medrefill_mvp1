# Architecture Diagram

This diagram illustrates the high-level architecture of the MedRefills AI platform.

```mermaid
graph TD
    subgraph "User's Browser"
        A[React Frontend]
    end

    subgraph "Cloud Infrastructure (Docker)"
        B[Nginx]
        C[FastAPI Backend]
        D[PostgreSQL DB]
        E[Redis Cache]
        F[AI Agent Service]
    end

    subgraph "External Systems"
        G[EMR/EHR System API]
    end

    A --"HTTPS API Calls"--> B
    B --"Reverse Proxy"--> C
    C --"Reads/Writes"--> D
    C --"Caches Sessions/Tasks"--> E
    C --"Initiates Review"--> F
    F --"Fetches Patient Data"--> G

    style A fill:#61DAFB,stroke:#000,stroke-width:2px
    style C fill:#009688,stroke:#000,stroke-width:2px
    style F fill:#9C27B0,stroke:#000,stroke-width:2px
    style D fill:#336791,stroke:#000,stroke-width:2px
    style E fill:#D82C20,stroke:#000,stroke-width:2px
    style G fill:#795548,stroke:#000,stroke-width:2px
```

### Description

*   **User's Browser**: The clinical staff interacts with our system through a React-based single-page application.
*   **Cloud Infrastructure**: All our backend services are containerized using Docker for consistency and scalability.
    *   **Nginx**: Acts as a reverse proxy, directing traffic to the appropriate backend service.
    *   **FastAPI Backend**: The core of our application, handling business logic, API requests, and database interactions.
    *   **PostgreSQL DB**: Our primary database for storing all persistent data like patient info, refill requests, and user accounts.
    *   **Redis Cache**: Used for caching frequently accessed data and managing background tasks to ensure a speedy user experience.
    *   **AI Agent Service**: A dedicated service that runs our AI agents to review refill requests.
*   **External Systems**: We connect to external Electronic Medical Record (EMR) systems to fetch patient data.
