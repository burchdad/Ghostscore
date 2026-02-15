# GhostScore - FICO Simulator, Optimizer & Credit Strategy Engine

An AI-powered FICO credit score simulator, optimizer, and credit strategy engine. Understand what impacts your credit score and simulate strategies to improve it.

**Status**: MVP Phase 1 - Core Scoring Engine & Web Interface

---

## 🎯 Features

### Phase 1 MVP (Current)
- ✅ FICO Score Estimation (300-850)
- ✅ Subscore Breakdown (5 factors)
- ✅ Account Management (credit cards, loans, mortgages)
- ✅ Scenario Simulation (paydown scenarios)
- ✅ Smart Recommendations (actionable strategies)
- ✅ Beautiful Dashboard with Charts

### Phase 2 (Advanced)
- Azure-trained ML model for better accuracy
- Score prediction timeline
- GPT AI advisor for personalized guidance
- Historical tracking

### Phase 3 (Ghost Integration)
- Integration with Ghost AI platform
- Automated credit strategy execution
- Multi-account management across institutions

---

## 🏗️ Architecture

```
Frontend (Next.js 14 + React)
         ↓
    API Layer (FastAPI)
         ↓
Scoring Engine (Python)
         ↓
Database (Supabase PostgreSQL)
```

### Tech Stack

**Frontend**
- Next.js 14
- React 18
- Tailwind CSS
- Recharts (visualizations)
- Zustand (state management)

**Backend**
- FastAPI
- Python 3.9+
- Pydantic

**Database**
- PostgreSQL (via Supabase)
- Optional: SQLAlchemy ORM

---

## 📁 Project Structure

```
ghostscore/
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── Dashboard.tsx
│   │   ├── ScoreCard.tsx
│   │   ├── SubscoreChart.tsx
│   │   ├── AccountsList.tsx
│   │   ├── AddAccountForm.tsx
│   │   ├── RecommendationsPanel.tsx
│   │   └── ScenarioSimulator.tsx
│   ├── lib/
│   │   ├── store.ts (Zustand store)
│   │   └── api.ts (API client)
│   ├── package.json
│   └── tsconfig.json
│
├── backend/
│   ├── main.py
│   ├── scoring/
│   │   ├── fico_engine.py
│   │   ├── subscores.py
│   │   ├── scenarios.py
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   └── schema.sql
│
├── docs/
│   └── (API documentation)
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 12+ (or Supabase account)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run server
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

API Docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Run dev server
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## 📊 API Endpoints

### Calculate Score
```
POST /score
Content-Type: application/json

{
  "accounts": [
    {
      "id": "card1",
      "type": "credit_card",
      "name": "Chase Sapphire",
      "balance": 2500,
      "limit": 5000,
      "open_date": "2020-01-15",
      "status": "active"
    }
  ],
  "derogatories": []
}

Response: {
  "score": 650,
  "payment_history": 75,
  "utilization": 70,
  "age": 60,
  "new_credit": 80,
  "mix": 65
}
```

### Simulate Paydown
```
POST /simulate/paydown

{
  "profile": { ... },
  "account_id": "card1",
  "new_balance": 1250
}

Response: {
  "original_score": 650,
  "new_score": 668,
  "score_delta": 18
}
```

### Get Recommendations
```
POST /recommendations

Response: {
  "current_score": 650,
  "estimated_potential_gain": 85,
  "recommendations": [
    {
      "action": "paydown",
      "account": "Chase Sapphire",
      "current_balance": 2500,
      "target_balance": 450,
      "amount_to_pay": 2050,
      "score_gain": 35,
      "priority": "high"
    }
  ]
}
```

---

## 🧮 FICO Score Model

### Scoring Factors

| Factor | Weight | Details |
|--------|--------|---------|
| Payment History | 35% | On-time payments, late payments, collections |
| Credit Utilization | 30% | % of available credit in use |
| Age of Credit | 15% | Average account age & oldest account |
| New Credit | 10% | Recent inquiries & new accounts |
| Credit Mix | 10% | Variety of account types |

### Score Range
- 300-579: Poor
- 580-669: Fair  
- 670-739: Good
- 740-799: Very Good
- 800-850: Excellent

---

## 📝 Environment Setup

### Backend (.env)
```
ENVIRONMENT=development
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=postgresql://user:password@localhost:5432/ghostscore
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🔄 Development Workflow

1. **Run Backend**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Run Frontend**
   ```bash
   cd frontend
   npm install && npm run dev
   ```

3. **Test API**
   Visit `http://localhost:8000/docs` for interactive API testing

4. **Access App**
   Visit `http://localhost:3000` in browser

---

## 🗄️ Database Setup

### Using Supabase (Recommended)

1. Create Supabase project
2. Go to SQL Editor
3. Copy and run [database/schema.sql](database/schema.sql)
4. Update `.env` with Supabase credentials

### Local PostgreSQL

```bash
# Create database
createdb ghostscore

# Run schema
psql ghostscore < database/schema.sql
```

---

# GhostScore

GhostScore is an open-source FICO-like credit score simulator, optimizer, and strategy engine. It provides a FastAPI backend with a Next.js frontend and tools to simulate paydown scenarios, estimate subscores, and generate recommendations.

This repository contains a working MVP and developer tooling for local development, testing, and CI.

## Quick links

- API server: `backend/main.py`
- Frontend: `frontend/`
- Database schema: `database/schema.sql`
- Alembic migrations: `backend/alembic/`
- CI workflow: `.github/workflows/ci.yml`

## Getting started (recommended: Docker)

1. Copy environment example and adjust values:

```bash
cp .env.example .env
```

2. Start database and backend with Docker Compose (applies migration manually unless `MIGRATE_ON_STARTUP` is enabled):

```bash
docker-compose up -d db
docker-compose build backend
docker-compose up -d backend
```

3. Verify API at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

Notes:
- To apply migrations on startup set `MIGRATE_ON_STARTUP=true` in your `.env` (default: `false`).
- The Postgres init SQL file is mounted from `database/schema.sql` in `docker-compose.yml`.

## Local development (without Docker)

Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn main:app --reload
```

Frontend

```bash
cd frontend
npm ci
npm run dev
```

Frontend runs at `http://localhost:3000` by default.

## Database migrations

- Migrations are managed with Alembic under `backend/alembic/` and an initial migration is included at `backend/alembic/versions/0001_initial.py`.
- To run migrations locally (inside project root):

```bash
# from project root
export DATABASE_URL=postgresql://user:pass@localhost:5432/ghostscore
alembic -c backend/alembic.ini upgrade head
```

## Tests

Backend

```bash
cd backend
pytest -q
```

Frontend

```bash
cd frontend
npm ci
npm test
```

CI is configured in `.github/workflows/ci.yml` to run backend tests and build the frontend on PRs and pushes to `main`.

## Linting & Formatting

- Python: `black`, `isort`, and `ruff` are configured. A `.pre-commit-config.yaml` is included; run `pre-commit install`.
- Frontend: use `npm run lint` via Next.js built-in linter.

## Generating API docs

The FastAPI OpenAPI JSON can be exported using `scripts/generate_openapi.py` which writes `docs/openapi.json`.

## Contributing

See `CONTRIBUTING.md` for development and PR guidelines.

## Next suggested additions

- Secrets management / GitHub Secrets + `.env` guidance
- CI: test coverage thresholds and artifact uploads (coverage.xml) — coverage thresholds are now enforced in CI (backend 80%).
- Dependabot configured in `.github/dependabot.yml` to keep dependencies up-to-date weekly.
- Add integration/e2e tests (Playwright)
- Monitoring: add basic Prometheus metrics + health endpoints
- Docker image publishing and release workflow
- Harden startup: migrations are opt-in via `MIGRATE_ON_STARTUP`, consider adding feature flags

Phase 2 is scoped and locked in — see [PHASE2.md](PHASE2.md) for milestones and acceptance criteria.

If you want, I can now scaffold issue templates and a project board for Phase 2.

---

MIT License — see `LICENSE`
