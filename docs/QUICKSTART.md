# GhostScore - Quick Start Commands

## One-Time Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env

# Initialize database (SQLite, zero-setup)
python init_db.py
# Select 'y' for sample family data (optional)
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
```

---

## Daily Development

### Start Backend
```bash
cd backend
source venv/bin/activate  # or: . venv/bin/activate
uvicorn main:app --reload
# API at http://localhost:8000
```

### Start Frontend (in new terminal)
```bash
cd frontend
npm run dev
# App at http://localhost:3000
```

### Test API
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Build & Run

### Production Backend
```bash
cd backend
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Production Frontend
```bash
cd frontend
npm run build
npm start
```

---

## Database (Phase 2+)

### Create Local PostgreSQL DB
```bash
createdb ghostscore
psql ghostscore < database/schema.sql
```

### Using Supabase
1. Create project at supabase.com
2. Run `database/schema.sql` in SQL editor
3. Add `SUPABASE_URL` and `SUPABASE_KEY` to backend `.env`

---

## Common Commands

| Task | Command |
|------|---------|
| Format code | `npm run lint` (frontend) |
| Check types | `tsc --noEmit` (frontend) |
| Test API endpoint | `curl http://localhost:8000/docs` |
| View API logs | Terminal where `uvicorn` is running |
| View frontend logs | Browser DevTools Console |

---

## Debugging

### Frontend
- Open DevTools (F12)
- Check Network tab for API calls
- Console for JavaScript errors

### Backend
- Check terminal output where `uvicorn` is running
- Add `print()` statements for debugging
- Use FastAPI docs at `/docs` to test endpoints

---

## Stop Servers

Press `Ctrl+C` in each terminal where a server is running.

---

## Reset Everything

```bash
# Kill Python processes
pkill -f uvicorn

# Clear Next.js cache
cd frontend && rm -rf .next && npm run dev &

# Start fresh
cd backend && source venv/bin/activate && uvicorn main:app --reload
```

---

Good to go! Run both servers and visit http://localhost:3000 🚀
