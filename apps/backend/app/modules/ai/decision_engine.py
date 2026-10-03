from app.modules.ai.schemas import AISignalInput, AIRiskAssessmentResponse, EmergencyRiskLevel

class EmergencyDecisionEngine:
    WEIGHTS = {"activity": 0.25, "voice": 0.25, "vision": 0.25, "sensor": 0.25}

    def assess(self, signals: AISignalInput) -> AIRiskAssessmentResponse:
        values = {
            "activity": signals.activity_score,
            "voice": signals.voice_score,
            "vision": signals.vision_score,
            "sensor": signals.sensor_score,
        }
        score = round(sum(values[k] * self.WEIGHTS[k] for k in values), 4)
        contributing = [k for k, value in values.items() if value >= 0.60]
        if score >= 0.85:
            level, action = EmergencyRiskLevel.CRITICAL, "Create emergency and initiate immediate response workflow."
        elif score >= 0.65:
            level, action = EmergencyRiskLevel.HIGH, "Create emergency and notify the response pipeline."
        elif score >= 0.40:
            level, action = EmergencyRiskLevel.MEDIUM, "Request confirmation or collect additional signals."
        else:
            level, action = EmergencyRiskLevel.LOW, "Continue monitoring; do not create an emergency automatically."
        return AIRiskAssessmentResponse(
            risk_score=score, risk_level=level, recommended_action=action,
            contributing_signals=contributing,
        )
