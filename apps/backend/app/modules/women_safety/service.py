import uuid

from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.database.models.women_safety_profile import WomenSafetyProfile
from app.database.models.family_group import FamilyGroup
from app.database.models.family_member import FamilyMember
from app.database.models.notification import Notification
from app.modules.women_safety.exceptions import (
    WomenSafetyDisabled,
    WomenSafetyProfileExists,
    WomenSafetyProfileNotFound,
)
from app.modules.women_safety.repository import WomenSafetyRepository
from app.modules.women_safety.schemas import (
    WomenSafetyProfileCreate,
    WomenSafetyProfileUpdate,
    WomenSafetySOSRequest,
)


class WomenSafetyService:
    def __init__(self, repository: WomenSafetyRepository):
        self.repository = repository

    def create_profile(self, user_id, request: WomenSafetyProfileCreate):
        if self.repository.get_by_user_id(user_id):
            raise WomenSafetyProfileExists()

        profile = WomenSafetyProfile(
            user_id=user_id,
            enabled=request.enabled,
            safe_word=request.safe_word,
            auto_share_location=request.auto_share_location,
        )
        self.repository.create(profile)
        self.repository.commit()
        self.repository.refresh(profile)
        return profile

    def get_profile(self, user_id):
        profile = self.repository.get_by_user_id(user_id)
        if profile is None:
            raise WomenSafetyProfileNotFound()
        return profile

    def update_profile(self, user_id, request: WomenSafetyProfileUpdate):
        profile = self.get_profile(user_id)

        for field, value in request.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        self.repository.commit()
        self.repository.refresh(profile)
        return profile

    def trigger_sos(self, user_id, request: WomenSafetySOSRequest):
        profile = self.get_profile(user_id)
        if not profile.enabled:
            raise WomenSafetyDisabled()

        emergency = Emergency(
            citizen_id=user_id,
            emergency_type="WomenSafetySOS",
            severity="High",
            status="Pending",
            latitude=request.latitude,
            longitude=request.longitude,
            description=request.description or "Women safety SOS activated.",
        )
        self.repository.db.add(emergency)
        self.repository.db.flush()

        self.repository.db.add(
            EmergencyUpdate(
                emergency_id=emergency.id,
                updated_by=user_id,
                status="Pending",
                remarks="Women Safety SOS activated.",
            )
        )

        recipients = (
            self.repository.db.query(FamilyMember.user_id)
            .join(FamilyGroup, FamilyGroup.id == FamilyMember.family_group_id)
            .filter(FamilyGroup.created_by == user_id)
            .all()
        )
        recipient_ids = {row[0] for row in recipients}

        for recipient_id in recipient_ids:
            self.repository.db.add(
                Notification(
                    recipient_id=recipient_id,
                    emergency_id=emergency.id,
                    notification_type="WomenSafetySOS",
                    title="Women Safety SOS",
                    message="A women safety SOS has been activated. Emergency location is available in the emergency record.",
                    channel="InApp",
                    is_read=False,
                )
            )

        try:
            self.repository.db.commit()
        except Exception:
            self.repository.db.rollback()
            raise

        return emergency, profile.auto_share_location
