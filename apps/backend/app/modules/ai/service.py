from app.database.models.emergency import Emergency
from app.database.models.emergency_update import EmergencyUpdate
from app.modules.ai.decision_engine import EmergencyDecisionEngine
from app.modules.ai.schemas import AIEmergencyDetectionRequest, AIEmergencyDetectionResponse, AISignalInput

class AIService:
    def __init__(self, db):
        self.db = db
        self.engine = EmergencyDecisionEngine()

    def assess(self, signals: AISignalInput):
        return self.engine.assess(signals)

    def detect_and_create(self, citizen_id, request: AIEmergencyDetectionRequest):
        assessment = self.engine.assess(request)
        should_create = assessment.risk_level.value in {"High", "Critical"}
        if not should_create:
            return AIEmergencyDetectionResponse(
                **assessment.model_dump(), emergency_id=None, emergency_created=False
            )

        emergency = Emergency(
            citizen_id=citizen_id,
            emergency_type=request.emergency_type,
            severity=assessment.risk_level.value,
            status="Pending",
            latitude=request.latitude,
            longitude=request.longitude,
            description=request.description or "Emergency detected by LifeLink AI.",
        )
        self.db.add(emergency)
        self.db.flush()
        self.db.add(EmergencyUpdate(
            emergency_id=emergency.id,
            updated_by=citizen_id,
            status="Pending",
            remarks=f"AI emergency detection. Risk score: {assessment.risk_score}; level: {assessment.risk_level.value}.",
        ))
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return AIEmergencyDetectionResponse(
            **assessment.model_dump(), emergency_id=emergency.id, emergency_created=True
        )
