# LifeLink AI — Day 5 Deployment and Demo Readiness

This checklist is for validating the existing single Flutter application with role-based dashboards and the FastAPI backend. It does not authorize merging PR #16; keep that pull request Draft/Open until validation is complete.

## Automated checks

- [ ] Backend Validation passes on the latest `feature/backend-composition` commit.
- [ ] Flutter Validation passes on the same commit.
- [ ] Backend logs show Python compilation, application import, migrations, tests, and Alembic head verification succeeded.
- [ ] Confirm the backend end-to-end flow: Citizen creates an emergency, unauthorized roles are denied dispatch/admin access, Police dispatches, Responder progresses the assignment, Hospital inventory is reserved and released.
- [ ] Confirm PR #16 remains open, draft, and unmerged.

## Backend environment

Configure these values in the deployment secret manager (never commit real secrets):

- Required application settings: `PROJECT_NAME`, `PROJECT_VERSION`, `API_V1_PREFIX`, `ENVIRONMENT`, `DEBUG`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
- PostgreSQL: `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
- Redis: `REDIS_HOST`, `REDIS_PORT`.
- Firebase push (optional until configured): set `FCM_ENABLED=true` only after supplying valid `FIREBASE_PROJECT_ID` and `FIREBASE_CREDENTIALS_JSON`. Keep `FCM_ENABLED=false` if no valid Firebase Admin service account is configured.

For production, set `DEBUG=false`, use a strong unique secret key, restrict database/network access, and configure HTTPS. Do not use the example development credentials in a deployment.

## Live smoke test

Use dedicated non-production test accounts for each role; do not use real emergency records or public emergency services.

1. Log in as Citizen and create a clearly labelled test emergency with test coordinates.
2. Confirm Citizen can view its status/timeline and cannot access Admin-only or Police-only operations.
3. Log in as Police and dispatch the test emergency.
4. Log in as the assigned Responder and verify Accepted → EnRoute → OnScene → Completed.
5. Confirm Citizen status updates and responder GPS tracking when location permission is granted.
6. Confirm Hospital resource count decreases on reservation and returns after completion/cancellation.
7. Confirm notification is persisted in the in-app inbox. If FCM is enabled, verify delivery on a real configured device and check server logs for provider failures.
8. Cancel or complete all test records and verify no active assignment/resource reservation remains.

## Flutter mobile and notification checks

- [ ] Verify Firebase client configuration exists for the target platform before expecting mobile push notifications.
- [ ] Verify Android/iOS notification permissions and token registration.
- [ ] Verify token refresh and logout/unregistration behaviour.
- [ ] Verify realtime reconnect/resync and app behaviour when GPS permission or network connectivity is unavailable.
- [ ] Test the role-specific screens within the same Flutter app; do not split roles into separate apps.

## What cannot be certified from repository CI alone

GitHub Actions unit/validation jobs do not prove a live deployment is reachable, Firebase credentials are valid, real devices receive push notifications, or production service configuration is secure. Mark those items complete only after running the live checks above and recording the result.
