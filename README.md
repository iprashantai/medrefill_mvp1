# MedRefills AI - MVP

AI-powered medication refill automation system for IgniteHealth.

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+)
- **SQLModel** (ORM)
- **PostgreSQL** (Database)
- **LangChain** (AI agents)
- **Celery & Redis** (Async tasks)

### Frontend
- **React 18** (Vite)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** (UI components)
- **TanStack Query** (Data fetching)

### DevOps
- **Docker** & **Docker Compose**

## Project Structure

```
mvp_v1/
├── docker-compose.yml          # Docker orchestration
├── backend/                     # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entrypoint
│       ├── models.py           # SQLModel database models
│       ├── schemas.py          # Pydantic schemas
│       ├── core/
│       │   └── db.py           # Database setup
│       ├── api/v1/
│       │   └── refill_requests.py  # API endpoints
│       ├── services/
│       │   └── emr_service.py  # Mock EMR service
│       └── agents/
│           ├── tools.py        # ProtocolCheckTool
│           └── medrefill_agents.py  # AI agents
└── frontend/                    # React frontend
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── App.tsx             # Main app with routing
        ├── main.tsx
        ├── services/
        │   └── api.ts          # API client
        ├── hooks/
        │   └── useRefillQueue.ts  # React Query hooks
        └── pages/
            ├── RefillQueuePage.tsx
            └── RefillDetailPage.tsx
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini Pro API key (for LangChain agent)

### 1. Environment Variables

Create a `.env` file in the root directory (optional, defaults are provided):

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://ignitehealth:ignitehealth@db:5432/medrefills
REDIS_URL=redis://redis:6379/0
```

### 2. Build and Run with Docker

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

**Note:** Modern Docker Desktop uses `docker compose` (with a space) instead of `docker-compose` (with a hyphen). If you have an older version, you may need to use `docker-compose` instead.

The services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Database Setup

The database tables are automatically created on backend startup via `create_db_and_tables()`.

### 4. Seed Initial Data (Optional)

A seed script is provided to populate the database with sample data:

```bash
# Run the seed script inside the backend container
docker compose exec backend python -m app.scripts.seed_db
```

This will create:
1. **2 Patients** (MRN: "12345" for Deny case, "67890" for Approve case)
2. **2 Medication Protocols** (SGLT2 Inhibitor and GLP-1 Agonist with rules)
3. **2 Refill Requests** (automatically processed by AI and set to pending human review)

Alternatively, you can use the FastAPI interactive docs at http://localhost:8000/docs to create data manually.

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on http://localhost:5173 with hot-reload.

## API Endpoints

### GET `/api/v1/refill-queue`
Returns all refill requests pending human review, sorted with "Deny" recommendations first.

### GET `/api/v1/refill-request/{request_id}`
Returns detailed information about a specific refill request, including:
- Request details
- Patient data (from mock EMR)
- Clinical data (visits, labs)
- Protocol check results

### POST `/api/v1/refill-request/{request_id}/review`
Submit a human review decision.

**Request Body:**
```json
{
  "decision": "Approve" | "Deny",
  "user_id": "clinical_staff_member"
}
```

## Features

### AI-Powered Review
- **ProtocolCheckTool**: Custom LangChain tool that evaluates medication protocols against patient EMR data
- **Primary Agent**: Uses Google Gemini Pro to review refill requests and make recommendations

### Human-in-the-Loop (HITL) Dashboard
- **Refill Queue**: Lists all pending requests with AI recommendations
- **Detail Page**: Comprehensive view showing:
  - AI decision and reasoning
  - Patient information
  - Protocol checks with pass/fail status
  - EMR clinical data
  - Approve/Deny action buttons

### Mock EMR Service
The `emr_service.py` provides mock patient and clinical data:
- **MRN "12345"**: Deny case (last visit >12 months ago, A1c 7.8)
- **MRN "67890"**: Approve case (recent visit, A1c 6.5)

## Notes

- The EMR service is mocked for MVP purposes. In production, this would connect to a real EMR system.
- The AI agent uses Google's Gemini Pro. Ensure your `GEMINI_API_KEY` is set.
- The frontend expects the backend to be running on `http://localhost:8000` (or configured via `VITE_API_URL`).

## Troubleshooting

1. **Backend won't start**: Check that PostgreSQL and Redis containers are healthy
2. **Frontend can't connect**: Verify the backend is running and CORS is configured
3. **AI agent errors**: Ensure `GEMINI_API_KEY` is set correctly. You can get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. **Database connection issues**: Check that the database container is running and credentials match

## License

Proprietary - IgniteHealth MVP

