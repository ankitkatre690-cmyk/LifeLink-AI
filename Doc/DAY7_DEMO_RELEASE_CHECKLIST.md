# LifeLink AI — Day 7 Demo and Release Readiness

**Scope:** Final demo preparation for the existing single Flutter application with role-based experiences and the FastAPI backend. This is a release-readiness checklist, not a claim that live device/deployment checks have already passed.

## 1. Release guardrails

- [ ] Keep PR #16 **Draft, Open, and Unmerged** until all required validation is reviewed.
- [x] Backend Validation workflow passed for commit `aa5880a55ccd7b275241391aac2e9c0d2d741988` (recorded on 2026-10-10).
- [x] Flutter Validation workflow passed in the PR run associated with the same PR; verify the latest commit status before presenting a release claim.
- [ ] Re-run/confirm both CI workflows after the Day 7 commit.
- [ ] Confirm migrations and tests pass against a clean CI PostgreSQL service.
- [ ] Do not use real emergency data, real patients, or public emergency services in a demo.

## 2. Demo environment readiness

### Backend
- [ ] Docker engine is running and PostgreSQL is reachable on the configured host port.
- [ ] Redis is reachable if enabled by the local environment.
- [ ] Copy `apps/backend/.env.example` to `.env` in `apps/backend` and use local-only credentials.
- [ ] Confirm `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` match the actual database container.
- [ ] Keep `FCM_ENABLED=false` unless valid Firebase Admin credentials and client platform configuration are installed.
- [ ] Start backend from `apps/backend` using the active virtual environment: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
- [ ] Check `http://127.0.0.1:8000/docs` and verify the expected API routes appear.
- [ ] Check a health endpoint if one is configured; do not assume a route exists without verifying it.

### Flutter
- [ ] From `apps/frontend`, run `flutter pub get`, `flutter analyze`, and `flutter test`.
- [ ] If generated platform scaffolding is absent, run `flutter create .` and review generated files before committing.
- [ ] For browser testing, configure the API base URL to `http://127.0.0.1:8000/api/v1`; ensure backend CORS permits the local development origin.
- [ ] For Android emulator testing, the API host is normally `http://10.0.2.2:8000/api/v1`.
- [ ] Verify location permission prompts and the SOS confirmation step.
- [ ] Verify login failures, offline states, loading states, empty lists, and retry paths do not leave the UI stuck.
- [ ] Verify WebSocket reconnect/resynchronization behavior when the network is interrupted.
- [ ] Do not expect push notifications until Firebase client configuration and backend credentials are valid.

## 3. Role-by-role demo flow

Use dedicated demo accounts and clearly labelled test records only.

1. **Citizen:** sign in, grant location permission if appropriate, review the SOS confirmation, create one test emergency, and open the tracking/timeline screen.
2. **Police:** sign in with a Police account, find the test emergency, create/update its case if needed, and initiate dispatch.
3. **Responder:** sign in as the assigned responder, inspect the assignment and distance/ETA, then advance through the supported assignment states (for example Accepted → EnRoute → OnScene → Completed).
4. **Hospital:** show incoming emergency information and the hospital resource availability/reservation behavior.
5. **Family:** show the available family-linked emergency status view only if the demo account is configured for it.
6. **Admin:** show the administrative view and verify role restrictions using non-admin accounts.
7. **Realtime and notifications:** show live assignment/status events and persisted in-app notifications. Demonstrate FCM only if it is actually configured and a test device receives it.
8. **Cleanup:** complete or cancel the test emergency, confirm there is no active assignment or stranded resource reservation, and sign out of all demo sessions.

Never simulate success by editing the database during the live walkthrough. If a service is unavailable, explain that dependency and show the relevant API/test evidence instead.

## 4. UI consistency review

- [ ] Consistent page titles, spacing, button styles, and status labels across role dashboards.
- [ ] Every network action displays a progress state and prevents accidental duplicate submission.
- [ ] Errors are understandable and provide a safe retry path; do not expose stack traces or secrets.
- [ ] Empty queues/resources have an explicit empty state rather than a blank page.
- [ ] Status colors are paired with text labels, not color alone.
- [ ] Permission denied, location unavailable, no network, and expired-session cases are handled.
- [ ] Accessibility review: readable contrast, sensible text scaling, semantic labels, and tap target sizes.
- [ ] No role-specific screen is presented as complete unless it exists in the current branch and has been verified.

## 5. Evidence to capture

- [ ] CI run URLs and exact commit SHA for backend and Flutter validation.
- [ ] API documentation screenshot with the backend running.
- [ ] One screenshot per role dashboard, using test data.
- [ ] Citizen SOS → Police dispatch → Responder lifecycle evidence.
- [ ] Hospital resource reservation/release evidence.
- [ ] Authorization denial evidence for at least one cross-role request.
- [ ] Known limitations and any skipped checks.

## 6. Known local blocker and recovery notes

During local verification, Docker Desktop failed to start with a `vpnkit-bridge handshake failed` error and `docker version` reported that the engine was unavailable. Consequently, the local PostgreSQL connection and login flow cannot currently be certified. Keep this as **blocked**, not passed.

Safe diagnostic sequence:
1. Check `wsl --status`, `wsl --version`, and `wsl --list --verbose`.
2. Check whether Docker Desktop is installed and whether its service exists.
3. Retry Docker Desktop startup and inspect its diagnostic report if the engine still fails.
4. Once the engine starts, run `docker ps -a` and inspect existing containers/ports before changing anything.
5. Do not use factory reset, unregister WSL distributions, delete Docker data folders, drop database tables, or stamp Alembic to head as a troubleshooting shortcut.

## 7. Release decision

A release/demo can be called **ready** only after the required checks above are completed and evidence is recorded. Passing CI does not prove local Docker health, live deployment availability, Firebase delivery, mobile permissions, or real-device realtime behavior. Keep PR #16 Draft/Open/Unmerged until the team explicitly reviews validation and approves the next step.
