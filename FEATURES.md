
# GhostScore Full Feature Overview

GhostScore is a lender-grade, production-complete, AI-powered credit intelligence platform for simulation, optimization, analytics, and scenario planning. Below is a comprehensive list of all features, endpoints, and capabilities as of February 2026.

---

## Core Features

- Multi-model FICO scoring (FICO 8, FICO 9, FICO 10, linear)
- Per-model calibration engine (aligns with real credit report data)
- Timeline Realism Engine (realistic score projections, reporting delays)
- Goal Solver (multi-model, composite, Monte Carlo, explainability)
- Score Stability Index (volatility/consistency metric)
- Composite score endpoint (average/weighted multi-model)
- Full auditability: model versioning, score hash, profile snapshotting
- Persistent score and scenario history (per model/version)
- ML-powered action sequencing and predictive score forecasting
- Advanced analytics: radar, trends, scenario comparison, PDF export
- Modern Next.js/React dashboard with all analytics and controls
- Subscore Breakdown (5 FICO factors)
- Account Management (credit cards, loans, mortgages)
- Scenario Simulation (paydown, payoff, derogatory removal)
- Smart Recommendations (actionable strategies)
- Multi-action scenario simulation (realistic combinations)
- Confidence intervals (optimistic/realistic/conservative projections)
- Optimal action sequencing (ML-driven, maximizes gain per unit effort)
- Priority matrix (quick wins vs strategic actions)
- Real-time score updates on scenario changes
- Scenario History & Comparison (persistent, multi-select, side-by-side)
- Pinning & Favorites for scenarios
- Timeline Visualization (score evolution over time)
- Export & Reporting (profile, action plan, scenario comparison as PDF)
- Scenario Tagging, Notes, and Feedback (editable, persistent)
- Scenario Analytics & Improvement Tracking (persistent, reviewable)
- Credit report upload/import (Equifax, Experian, etc.)
- Advisor network integration (planned)
- Mobile app (planned)

---

## API Endpoints

- `/score` — Calculate FICO score and subscores
- `/score/multi` — Multi-model scoring (returns scores, version, hash for each model)
- `/score/composite` — Composite score endpoint (average/weighted multi-model)
- `/score/stability` — Score Stability Index endpoint
- `/score/forecast` — ML-driven predictive score forecasting (week-by-week)
- `/score/all` — All model scores (for comparison)
- `/simulate/paydown` — Simulate score change from paying down an account
- `/recommendations` — Get optimization recommendations
- `/optimize` — AI-powered action ranking and improvement timeline
- `/optimize/goal` — Goal Solver (multi-model, composite, Monte Carlo, explainability)
- `/profiles/{profile_id}/scenario_history` — Save scenario run
- `/profiles/{profile_id}/scenario_history?limit=100` — Retrieve scenario history
- `/profiles/{profile_id}/scenario_history/{scenario_id}` — Update notes/tags
- `/profiles/{profile_id}/scenario_history/{scenario_id}/pin` — Pin/unpin scenario
- `/profiles/{profile_id}/scenario_history/{scenario_id}/feedback` — Add/update feedback
- `/profiles/{profile_id}/export/pdf` — Export profile PDF
- `/profiles/{profile_id}/action_plan/pdf` — Export action plan PDF
- `/profiles/{profile_id}/scenario_comparison/pdf?scenario_ids=ID1,ID2` — Export scenario comparison PDF
- `/profiles/{profile_id}/calibrate` — Calibrate profile with real score (per model)
- `/profiles/{profile_id}/accounts` — Add account
- `/profiles/{profile_id}/derogatories` — Add derogatory mark
- `/profiles/{profile_id}/upload-credit-report` — Upload credit report
- `/profiles/{profile_id}/import-accounts-from-report` — Import accounts from report

---

## Frontend Components

- Dashboard (all analytics, actions, downloads, calibration)
- ScoreCard (score and subscore breakdown)
- SubscoreChart (visualizes 5 FICO factors)
- AccountsList (overview of accounts)
- AddAccountForm (add new accounts)
- RecommendationsPanel (quick actions)
- CreditReportUpload (upload/import credit reports)
- ProfileSelector (switch between profiles)
- ScenarioSimulator (multi-action simulation)
- ScoreTrajectoryChart (week-by-week improvement timeline)
- ScoreTrends (historical score visualization)
- ActionPriorityList (ranked recommendations, multi-select)
- SimulatorSlider (interactive paydown simulation)
- ScoreFactorsRadar (radar chart of subscores)
- ScenarioHistory (persistent scenario tracking, comparison, tagging, notes, pinning, feedback)

---

## ML/AI Capabilities

- Action sequencing optimization (RandomForestClassifier)
- Predictive score forecasting (Ridge regression)
- Model persistence (joblib)
- Calibration engine (aligns estimates with real scores)
- Timeline Realism Engine (delayed/ramped score effects)
- Goal Solver (Monte Carlo simulation, multi-model, composite, explainability)
- Score Stability Index (volatility/consistency metric)
- Explainability engine (score factor explanations)
- Validation engine (score consistency, regression tests)

---

## Advanced Analytics

- Confidence intervals for scenario projections
- Priority matrix (quick wins vs strategic actions)
- Timeline visualization (score evolution)
- Scenario comparison (side-by-side PDF export)
- Persistent improvement tracking

---

## Export & Reporting

- Profile PDF export
- Action plan PDF export
- Scenario comparison PDF export

---

## Planned/Upcoming Features

- Mobile app (React Native)
- Advisor network integration
- Additional ML models for scenario analysis

---

## Tech Stack

- Frontend: Next.js 14, React 18, Tailwind CSS, Recharts, Zustand, Lucide React, React Hot Toast
- Backend: FastAPI, Python 3.9+, Pydantic, scikit-learn
- Database: PostgreSQL (Supabase), SQLAlchemy ORM, Alembic

---

For detailed API usage, see README.md and docs/API.md.
