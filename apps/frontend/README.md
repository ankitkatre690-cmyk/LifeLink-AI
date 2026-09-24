# LifeLink AI Flutter Frontend

This directory contains the single Flutter application for LifeLink AI.

## Architecture

- Flutter + Material 3
- Riverpod for application state
- GoRouter for navigation
- Dio for REST API communication
- Flutter Secure Storage for JWT/session storage

The application is a single role-aware client. Citizen, Family, Responder, Hospital, Police, and Admin experiences will be exposed through authenticated routes rather than separate applications.

## Backend

The default Android emulator API base URL is:

`http://10.0.2.2:8000/api/v1`

Override the API base URL through the application's configuration layer before production deployment.

## Current phase

This PR establishes the frontend foundation only. It intentionally does not yet implement authentication, Firebase Messaging, WebSockets, or role dashboards.

## Local setup

From the repository root:

```bash
cd apps/frontend
flutter pub get
flutter analyze
flutter test
```

If platform folders have not been generated yet, run `flutter create .` from `apps/frontend` before launching on Android, iOS, web, or desktop. Review generated platform changes before committing them.

## Planned next increments

1. Authentication and JWT session flow
2. Role-aware route guards
3. Citizen emergency flow
4. Family/responder/hospital/police/admin dashboards
5. Firebase Messaging and device-token registration
6. Authenticated WebSocket events
7. End-to-end emergency workflow
