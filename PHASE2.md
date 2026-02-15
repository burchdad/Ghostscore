# GhostScore Phase 2 — Scope & Milestones

This document locks in Phase 2 deliverables and milestones. Each item below should be tracked as an issue/PR and tied to CI where applicable.

Goals
- Improve score accuracy and provide timeline/prediction features
- Add user authentication and persistence
- Add richer analytics and historical tracking

Milestones

1) Authentication & Users (2 weeks)
   - Add Supabase (or Postgres + JWT) auth integration
   - Protect profile endpoints and add user ownership
   - E2E test for sign-up / profile creation

2) Persistence & Data (2 weeks)
   - Finalize DB schema changes (user profile history, transactions)
   - Add background job to persist score snapshots
   - Data migration scripts and tests

3) Scoring Improvements (3 weeks)
   - Calibrate scoring model with real-world heuristics
   - Add ML-ready data pipeline (optional)
   - Add uncertainty/variance bands to predictions

4) UX and Reporting (2 weeks)
   - Score timeline with historical trends
   - Exportable reports (PDF/CSV)
   - Notifications and recommendations UI

5) Integrations & Automation (3 weeks)
   - Add Open Banking / aggregation integrations (sandbox)
   - Add scheduled scenarios and strategy execution (opt-in)

Acceptance criteria
- Documented API for new endpoints
- Unit and integration tests covering new functionality
- CI gates for coverage and E2E tests

Risks & Notes
- Data privacy and security are paramount — treat any PII carefully.
- Consider feature flags for experimental scoring changes.

If you approve, I will scaffold issues and PR templates for these milestones and propose an initial timeline in the repo project board.
