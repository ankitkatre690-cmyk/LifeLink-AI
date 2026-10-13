# LifeLink AI

LifeLink AI is a single Flutter application with role-based experiences backed by a FastAPI service. Roles include Citizen, Family, Responder, Hospital, Police, and Admin. The system is designed around a shared emergency lifecycle, dispatch/assignment workflow, hospital resource handling, notifications, and authenticated realtime events.

> Development/demo software only. Do not use it as a substitute for official emergency services. Use test accounts and synthetic records for demos.

## Repository layout

- `apps/backend` — FastAPI API, SQLAlchemy models, Alembic migrations, and backend tests.
- `apps/frontend` — Flutter application, role-aware navigation, REST/realtime client, and Flutter tests.
- `Doc` — project specifications and day-by-day readiness documents.
- `.github/workflows` — backend and Flutter validation workflows.

## Local backend setup (PowerShell)

1. Start Docker Desktop and verify its engine is running.
2. Confirm existing PostgreSQL/Redis containers and published ports before creating or changing containers:
   ```powershell
   docker ps -a
   docker port lifelink-postgres
   ```
   The container name and host port may differ by machine; use the actual output.
3. Open PowerShell in `apps/backend` and create/activate a virtual environment:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
   Use the Python version supported by the current backend workflow. If Python 3.12 is not installed locally, install it or use the project's validated Python version.
4. Edit `.env` so PostgreSQL and Redis hosts/ports match the actual local services. Never commit real passwords, API keys, or Firebase service-account data.
5. Run migrations only after confirming the configured database is the intended development database and its migration history is compatible:
   ```powershell
   alembic upgrade head
   ```
6. Start the API:
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
7. Open `http://127.0.0.1:8000/docs` to inspect registered API routes.

## Local Flutter setup

From `apps/frontend`:

```powershell
flutter pub get
flutter analyze
flutter test
```

If platform folders are absent, run `flutter create .` and review generated changes before committing. For Chrome/web development, configure the API base URL as `http://127.0.0.1:8000/api/v1` and ensure backend CORS settings allow the local web origin. For an Android emulator, the usual host URL is `http://10.0.2.2:8000/api/v1`.

## Configuration

Backend settings are documented by `apps/backend/.env.example`. Local example values are for development only. Keep `FCM_ENABLED=false` unless both backend Firebase credentials and target Flutter platform configuration are set up. Missing Firebase configuration should not be mistaken for a successful push-delivery test.

## Validation

- Backend workflow: `.github/workflows/backend-validation.yml`
- Flutter workflow: `.github/workflows/flutter-validation.yml`
- Optional authenticated E2E workflow: `.github/workflows/flutter-e2e.yml` (requires test-environment secrets)

Run `Doc/DAY7_DEMO_RELEASE_CHECKLIST.md` before a demo. Record actual results rather than marking unchecked live checks complete based only on CI.

## Pull request status

PR #16 is intentionally **Draft/Open/Unmerged** until validation has been reviewed. Do not merge it as part of local setup.
