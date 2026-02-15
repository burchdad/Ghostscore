# GhostScore Database Setup Guide

## Overview

GhostScore uses **SQLAlchemy** as the ORM and defaults to **SQLite** for zero-setup (perfect for family use).

- **Default**: SQLite (`ghostscore.db` file - no setup needed)
- **Optional**: PostgreSQL for production

---

## Quick Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Copy Environment File
```bash
cp .env.example .env
```

### 3. Initialize Database
```bash
python init_db.py
```

When prompted, choose `y` to create sample family data:
- 1 user (family@ghostscore.local)
- 1 credit profile
- 3 sample accounts (2 credit cards + 1 auto loan)

---

## Database Options

### SQLite (Default - No Setup Required)
Perfect for family use. Everything stored in `ghostscore.db` file.

**Pros:**
- Zero setup
- No external dependencies
- Portable (single file)
- Great for development

**Cons:**
- Single user only (family works great!)
- Limited concurrency

**File:** `ghostscore.db` (created in `backend/` directory)

### PostgreSQL (Production Ready)
Use if you want to scale beyond family or need multiple concurrent users.

**Setup:**

```bash
# Install PostgreSQL
brew install postgresql  # macOS

# Start service
brew services start postgresql

# Create database
createdb ghostscore

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/ghostscore

# Run init script
python init_db.py
```

---

## Database Schema

Tables created:

| Table | Purpose |
|-------|---------|
| `users` | Family members |
| `credit_profiles` | Credit profiles (each user can have multiple) |
| `accounts` | Credit cards, loans, mortgages |
| `derogatories` | Late payments, collections, bankruptcies |
| `score_history` | Score calculation history (for trends) |

---

## Working with Database

### Initialize DB
```bash
python init_db.py
```

### Reset DB (Development)
Edit `init_db.py` and call `reset_db()` instead of `init_db()`.

Or in Python:
```python
from models.database import reset_db
reset_db()
```

---

## API Endpoints (Database-Backed)

### Create Profile
```bash
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{"email": "mom@family.local", "profile_name": "Mom Profile"}'
```

### Get All Profiles
```bash
curl http://localhost:8000/profiles/mom@family.local
```

### Get Full Profile
```bash
curl http://localhost:8000/profiles/{profile_id}/full
```

### Add Account
```bash
curl -X POST http://localhost:8000/profiles/{profile_id}/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "credit_card",
    "name": "Chase Sapphire",
    "balance": 2500,
    "limit": 5000,
    "open_date": "2020-01-15",
    "status": "active"
  }'
```

### Calculate Score (Still In-Memory)
```bash
# Note: Score calculation doesn't need DB - it just reads the profile
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{...profile...}'
```

---

## Environment Variables

```bash
# .env file

# Database URL
DATABASE_URL=sqlite:///./ghostscore.db

# Optional: Show SQL queries (debug)
SQL_ECHO=false

# Environment
ENVIRONMENT=development
```

---

## Troubleshooting

### Database locked error (SQLite)
SQLite has limited concurrency. This is fine for family use.
If you hit this in production, switch to PostgreSQL.

### Profile not found 404
Make sure you're using the correct profile ID returned from `/profiles` endpoint.

### Sample data not created
Run `python init_db.py` again and select `y`.

---

## For Development: Inspecting Database

### View SQLite Database
```bash
# Install sqlite CLI if needed
brew install sqlite

# Query database
sqlite3 backend/ghostscore.db

# In sqlite prompt:
> .tables
> SELECT * FROM users;
> SELECT * FROM credit_profiles;
> .exit
```

### Enable SQL Echo (Debug)
In `.env`, set:
```
SQL_ECHO=true
```

Then all SQL queries will print to console.

---

## Next Steps

1. ✅ Database initialized with sample data
2. ✅ All tables created
3. ✅ API endpoints wired to database
4. **Next**: Connect frontend to use `/profiles` and `/accounts` endpoints for data persistence
5. **Later**: Add score history tracking to show trends

---

## Migration to PostgreSQL (When Ready)

When you're ready to scale:

```bash
# 1. Install PostgreSQL locally or get a cloud instance
# 2. Create database: createdb ghostscore
# 3. Update .env:
DATABASE_URL=postgresql://user:password@hostname:5432/ghostscore
# 4. Run init_db.py
python init_db.py
```

SQLAlchemy handles the differences - your code stays the same! 🎉
