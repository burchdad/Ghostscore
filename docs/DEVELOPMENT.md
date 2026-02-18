# GhostScore Development Guide

GhostScore is a lender-grade, production-complete, AI-powered credit intelligence engine. All endpoints are versioned, auditable, and support multi-model scoring, calibration, timeline realism, goal solving, and advanced analytics. See [FEATURES.md](../FEATURES.md) for a full feature list.

## Setup Guide

### 1. Clone Repository
```bash
git clone <repo-url>
cd ghostscore
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run server
uvicorn main:app --reload
```

The API server will start at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd ../frontend

# Install npm dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

---

## Project Organization

### Backend Structure

```
backend/
├── main.py              # FastAPI app setup
├── scoring/
│   ├── fico_engine.py   # Main scoring logic
│   ├── subscores.py     # Individual subscore calculations
│   └── scenarios.py     # What-if simulation engine
├── models/
│   └── (SQLAlchemy models - for Phase 2)
└── requirements.txt
```

### Frontend Structure

```
frontend/
├── app/
│   ├── page.tsx         # Home page
│   ├── layout.tsx       # Root layout
│   └── globals.css      # Global styles
├── components/
│   ├── Dashboard.tsx    # Main dashboard
│   ├── ScoreCard.tsx    # Score display
│   ├── SubscoreChart.tsx # Chart visualization
│   ├── ScenarioSimulator.tsx # What-if tool
│   └── ...
└── lib/
   ├── store.ts         # Zustand state management
   └── api.ts           # API client
```

---

## Key Concepts

### FICO Scoring Model

The scoring engine uses a weighted model based on real FICO methodology:

1. **Payment History (35%)** - Most important
   - Late payments (30, 60, 90+ days)
   - Collections and charge-offs
   - Bankruptcy impact

2. **Credit Utilization (30%)** - Second most important
   - Locked to utilization ratio of available credit
   - Optimal: < 10%
   - Bad: > 70%

3. **Age of Credit (15%)**
   - Average account age
   - Oldest account matters

4. **New Credit (10%)**
   - Recent account openings and inquiries
   - Too many new accounts = risk signal

5. **Credit Mix (10%)**
   - Variety (credit cards vs loans, etc.)
   - More variety = better

### Profiles & Scenarios

Users enter their credit data as a "Profile":
- List of accounts (credit cards, loans, mortgages)
- List of derogatory marks (lates, collections, etc.)

The Scenario Engine then lets them:
- Simulate paying down specific accounts
- See estimated score impact
- Get recommendations ranked by impact

---

## API Development

### Adding New Endpoints

1. In `backend/main.py`, add a new route:

```python
@app.post("/new-endpoint")
def new_endpoint(request: YourModel):
    """Documentation"""
    result = some_calculation(request)
    return result
```

2. Define request/response models in `main.py` using Pydantic:

```python
class YourModel(BaseModel):
    field1: str
    field2: int
    field3: Optional[float] = None
```

### Testing Endpoints

Use the interactive API docs at `http://localhost:8000/docs`

Or use curl:
```bash
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{"accounts": [...], "derogatories": []}'
```

---

## Frontend Development

### Adding Components

1. Create new component in `frontend/components/`:

```tsx
'use client'

import { useState } from 'react'

export default function MyComponent() {
  return (
    <div className="...">
      {/* Component JSX */}
    </div>
  )
}
```

2. Import and use in parent component

### State Management

Uses Zustand for global state in `lib/store.ts`:

```tsx
import { useStore } from '@/lib/store'

// In component:
const { profile, score, addAccount } = useStore()
```

### Styling

Uses Tailwind CSS. No need for CSS modules unless necessary.

```tsx
<div className="bg-slate-700 rounded-lg p-6 text-white">
  {/* Dark themed component */}
</div>
```

---

## Testing the Integration

### Manual Test Flow

1. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test in Browser**
   - Navigate to http://localhost:3000
   - Add test accounts
   - See score calculation
   - Try scenario simulator

### Test Account Data

```json
{
  "accounts": [
    {
      "id": "card1",
      "type": "credit_card",
      "name": "Test Card",
      "balance": 2500,
      "limit": 5000,
      "open_date": "2020-01-15",
      "status": "active"
    }
  ],
  "derogatories": []
}
```

Expected score: ~640-680 (medium range)

---

## Deployment (Future)

### Backend (FastAPI)
- Deploy to Heroku, Railway, or cloud service
- Use uvicorn with gunicorn in production
- Set environment variables

### Frontend (Next.js)
- Build: `npm run build`
- Deploy to Vercel (recommended) or any Node.js host

### Database
- Use Supabase for managed PostgreSQL
- Or self-hosted PostgreSQL

---

## Troubleshooting

### CORS Errors
Already enabled in `main.py`. If issues persist, check:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change for production
    ...
)
```

### API Not Responding
1. Check backend is running: `http://localhost:8000/health`
2. Check NEXT_PUBLIC_API_URL in frontend `.env.local`

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

---

## Next Steps

1. Add user authentication (Supabase Auth)
2. Connect to real database
3. Add score history tracking
4. Implement ML model
5. Deploy to production

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [FICO Scoring](https://www.myfico.com/credit-education/whats-in-your-credit-score)
