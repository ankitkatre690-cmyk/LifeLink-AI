from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PushMessage:
    recipient_id: UUID
    title: str
    body: str
    data: dict[str, str]


class PushNotificationProvider:
    """
    Provider boundary for mobile push delivery.

    V1 deliberately does not send to Firebase until device-token storage and
    Firebase credentials are configured. This keeps notification persistence
    independent from an external provider.
    """

    def send(self, message: PushMessage) -> None:
        raise NotImplementedError


class FirebasePushNotificationProvider(PushNotificationProvider):
    """Placeholder for the Firebase Admin SDK implementation."""

    def send(self, message: PushMessage) -> None:
        raise RuntimeError("Firebase push delivery is not configured.")


class NoOpPushNotificationProvider(PushNotificationProvider):
    def send(self, message: PushMessage) -> None:
        return None


push_provider: PushNotificationProvider = NoOpPushNotificationProvider()
