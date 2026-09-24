from dataclasses import dataclass
import json
import logging
from uuid import UUID

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PushMessage:
    recipient_id: UUID
    title: str
    body: str
    data: dict[str, str]


class PushNotificationProvider:
    """Provider boundary for mobile push delivery."""

    def send(self, message: PushMessage, tokens: list[str]) -> list[str]:
        raise NotImplementedError


class NoOpPushNotificationProvider(PushNotificationProvider):
    """Safe provider used when FCM is not explicitly enabled."""

    def send(self, message: PushMessage, tokens: list[str]) -> list[str]:
        return []


class FirebasePushNotificationProvider(PushNotificationProvider):
    """Firebase Cloud Messaging provider using the Firebase Admin SDK."""

    def __init__(self) -> None:
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return

        if not settings.FIREBASE_CREDENTIALS_JSON:
            raise RuntimeError("FIREBASE_CREDENTIALS_JSON is required when FCM_ENABLED=true.")

        import firebase_admin
        from firebase_admin import credentials

        try:
            firebase_admin.get_app()
        except ValueError:
            credential_data = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            options = {}
            if settings.FIREBASE_PROJECT_ID:
                options["projectId"] = settings.FIREBASE_PROJECT_ID
            firebase_admin.initialize_app(
                credentials.Certificate(credential_data),
                options=options or None,
            )

        self._initialized = True

    def send(self, message: PushMessage, tokens: list[str]) -> list[str]:
        if not tokens:
            return []

        self._ensure_initialized()

        from firebase_admin import messaging

        invalid_tokens: list[str] = []
        for start in range(0, len(tokens), 500):
            batch = tokens[start:start + 500]
            response = messaging.send_each_for_multicast(
                messaging.MulticastMessage(
                    tokens=batch,
                    notification=messaging.Notification(
                        title=message.title,
                        body=message.body,
                    ),
                    data=message.data,
                )
            )
            for token, result in zip(batch, response.responses):
                if result.success:
                    continue
                code = getattr(result.exception, "code", "")
                if code in {
                    "messaging/registration-token-not-registered",
                    "messaging/invalid-registration-token",
                }:
                    invalid_tokens.append(token)
                else:
                    logger.warning(
                        "FCM delivery failed for recipient %s: %s",
                        message.recipient_id,
                        result.exception,
                    )

        return invalid_tokens


def build_push_provider() -> PushNotificationProvider:
    if settings.FCM_ENABLED:
        return FirebasePushNotificationProvider()
    return NoOpPushNotificationProvider()


push_provider: PushNotificationProvider = build_push_provider()
