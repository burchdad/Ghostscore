---
title: "Finalize DB schema and add score snapshot table"
labels: [backend, database]
milestone: Persistence & Data
---

Add tables and migrations for persistent score snapshots and any additional profile data.

- Add `score_snapshots` (profile_id, score, subscores, created_at)
- Create Alembic migrations and tests
