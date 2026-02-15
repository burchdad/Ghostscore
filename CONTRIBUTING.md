Thanks for contributing to Ghostscore! This file describes the basic workflow and expectations.

1. Setup

- Copy `.env.example` to `.env` and adjust values.
- Backend: create and activate a virtualenv then `pip install -r backend/requirements.txt`.
- Frontend: run `npm ci` in `frontend/`.

2. Code style

- Python: use `black` + `isort` + `ruff`. A pre-commit config is included; run `pre-commit install`.
- JS/TS: follow `frontend` lint rules (`npm run lint`).

3. Tests

- Backend tests live under `backend/tests/`. Run `pytest backend`.
- Frontend: add tests to `frontend/` and run with `npm test` when available.

4. Pull requests

- Open PRs against `main` with a clear title and description.
- CI will run lint, tests, and build checks.
