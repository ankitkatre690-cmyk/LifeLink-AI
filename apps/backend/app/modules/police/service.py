from datetime import datetime, timezone

from app.database.models.police_case import PoliceCase
from app.modules.police.exceptions import PoliceCaseExists, PoliceCaseNotFound
from app.modules.emergency.exceptions import EmergencyNotFound
from app.modules.police.repository import PoliceRepository
from app.modules.police.schemas import PoliceCaseCreate, PoliceCaseUpdate


ALLOWED_CASE_TRANSITIONS = {
    "Open": {"Closed", "Cancelled"},
    "Closed": set(),
    "Cancelled": set(),
}


class PoliceService:
    def __init__(self, repository: PoliceRepository):
        self.repository = repository

    def list_active_emergencies(self):
        return self.repository.list_active_emergencies()

    def create_case(self, emergency_id, police_user_id, request: PoliceCaseCreate):
        if self.repository.get_case_by_emergency(emergency_id):
            raise PoliceCaseExists()

        if self.repository.get_emergency(emergency_id) is None:
            raise EmergencyNotFound()

        case = PoliceCase(
            emergency_id=emergency_id,
            police_user_id=police_user_id,
            case_status="Open",
            notes=request.notes,
        )
        self.repository.create_case(case)
        self.repository.commit()
        self.repository.refresh(case)
        return case

    def get_case(self, case_id):
        case = self.repository.get_case(case_id)
        if case is None:
            raise PoliceCaseNotFound()
        return case

    def update_case(self, case_id, request: PoliceCaseUpdate):
        case = self.get_case(case_id)
        emergency = self.repository.get_emergency(case.emergency_id)
        if emergency is None:
            raise EmergencyNotFound()

        if request.case_status not in ALLOWED_CASE_TRANSITIONS:
            raise ValueError(f"Invalid police case status: {request.case_status}")

        if (
            request.case_status != case.case_status
            and request.case_status
            not in ALLOWED_CASE_TRANSITIONS.get(case.case_status, set())
        ):
            raise ValueError(
                f"Invalid police case status transition: "
                f"{case.case_status} -> {request.case_status}"
            )

        if case.case_status in {"Closed", "Cancelled"} and request.case_status == case.case_status:
            case.notes = request.notes
            self.repository.commit()
            self.repository.refresh(case)
            return case

        case.case_status = request.case_status
        case.notes = request.notes
        if request.case_status in {"Closed", "Cancelled"}:
            case.closed_at = datetime.now(timezone.utc)
            if not self.repository.has_active_assignment(case.emergency_id):
                emergency.status = "Completed" if request.case_status == "Closed" else "Cancelled"
        else:
            case.closed_at = None
        self.repository.commit()
        self.repository.refresh(case)
        return case
