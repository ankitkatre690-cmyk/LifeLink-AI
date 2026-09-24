# Push Notifications

LifeLink AI keeps in-app notifications as the source-of-record and adds FCM as an optional mobile delivery channel.

## Runtime behavior

1. A notification is persisted using the existing Notification model.
2. Active device tokens for the recipient are loaded from `device_tokens`.
3. When `FCM_ENABLED=false`, the NoOp provider is used and no external call is made.
4. When FCM is enabled, Firebase Admin sends the notification to the recipient's active tokens in batches of 500.
5. Firebase responses for unregistered/invalid tokens deactivate those tokens automatically.
6. Push delivery failures are logged and do not replace the in-app notification transaction.

## Firebase configuration

Set these backend environment variables only in a secure runtime environment:

- `FCM_ENABLED=true`
- `FIREBASE_PROJECT_ID` (optional when present in credentials)
- `FIREBASE_CREDENTIALS_JSON` containing the Firebase service-account JSON

Never commit service-account credentials to GitHub.

## Mobile integration still required

The Flutter application must initialize Firebase Messaging, request notification permission where required, obtain the FCM registration token, register it through `POST /api/v1/notifications/device-tokens`, and deactivate/refresh tokens when they change.
