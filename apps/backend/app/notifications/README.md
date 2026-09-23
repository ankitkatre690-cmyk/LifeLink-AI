# Notification Delivery

LifeLink AI persists notifications in PostgreSQL and exposes them through the notification API.

The push layer is provider-based:
- `NoOpPushNotificationProvider` is the safe default.
- `FirebasePushNotificationProvider` is the integration boundary for FCM.
- Actual Firebase credentials, device-token storage, and mobile registration are intentionally deferred until the Flutter client is implemented.

This prevents backend code from pretending that push delivery is active before the required mobile/device configuration exists.
