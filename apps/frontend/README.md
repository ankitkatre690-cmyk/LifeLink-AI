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

The frontend foundation now includes authentication, role-aware routing, Citizen emergency SOS with device location, authenticated WebSockets, and Firebase Messaging token registration.

### Location platform configuration

The repository intentionally does not commit generated Flutter platform folders yet. Before running the Android app, ensure the Android application manifest contains:

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

For iOS, add the location usage description to `Info.plist`:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>LifeLink AI uses your location to share your position during an emergency.</string>
```

Do not request background location for the current SOS flow. Background tracking will be designed separately if required.

### Firebase Cloud Messaging

The app registers the authenticated device's FCM token with the existing backend endpoint `/api/v1/notifications/device-tokens`. Token refresh is registered automatically, and the token is deactivated during logout when a registration ID is available.

Before mobile push can run, configure Firebase for the target platform using the official Firebase Flutter setup. The generated Firebase configuration files are intentionally not committed by this foundation increment. Do not commit Firebase service-account credentials or other private keys.

FCM initialization is isolated from authentication: missing Firebase configuration does not block login.

Foreground FCM messages are exposed through the notification service and displayed by the Citizen dashboard. When the app is backgrounded or terminated, Firebase Messaging handles notification delivery through the platform notification system after the Firebase platform configuration is installed.

The Firebase background handler is registered at application startup and intentionally performs no emergency-domain work. Emergency state remains owned by the backend and realtime channels.

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


### Responder realtime dispatch

The Responder dashboard listens for the existing `dispatch.assignment` realtime event. When received, it immediately displays the assignment ID, emergency ID, status, distance, and ETA. Assignment status changes continue through the existing responder REST endpoint.

The realtime backend/dispatch implementation is maintained on its dedicated backend feature branches and must be integrated into the release branch before this frontend listener can receive production dispatch events.