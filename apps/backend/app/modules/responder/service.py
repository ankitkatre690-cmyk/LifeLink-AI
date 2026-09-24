import uuid

from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.responder_location import ResponderLocation
from app.database.models.responder_profile import ResponderProfile
from app.modules.responder.exceptions import (
    AssignmentAlreadyExists,
    EmergencyAssignmentNotFound,
    EmergencyNotFound,
    InvalidResponderRole,
    ResponderProfileAlreadyExists,
    ResponderProfileNotFound,
)
from app.modules.responder.repository import ResponderRepository


ALLOWED_RESPONDER_STATUSES = {"Available", "Busy", "Offline"}

ALLOWED_ASSIGNMENT_STATUSES = {
    "Assigned",
    "Accepted",
    "EnRoute",
    "OnScene",
    "Completed",
    "Cancelled",
}

ALLOWED_ASSIGNMENT_TRANSITIONS = {
    "Assigned": {"Accepted", "Cancelled"},
    "Accepted": {"EnRoute", "Cancelled"},
    "EnRoute": {"OnScene", "Cancelled"},
    "OnScene": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}

EMERGENCY_STATUS_BY_ASSIGNMENT = {
    "Assigned": "Assigned",
    "Accepted": "Accepted",
    "EnRoute": "EnRoute",
    "OnScene": "OnScene",
    "Completed": "Completed",
    "Cancelled": "Cancelled",
}


class ResponderService:
    def __init__(self, repository: ResponderRepository):
        self.repository = repository

    def _ensure_responder_role(self, user):
        if user.role is None or user.role.name != "Responder":
            raise InvalidResponderRole()

    def create_profile(self, user, request):
        self._ensure_responder_role(user)

        if self.repository.get_profile_by_user_id(user.id):
            raise ResponderProfileAlreadyExists()

        profile = ResponderProfile(
            user_id=user.id,
            responder_type=request.responder_type,
            vehicle_number=request.vehicle_number,
            latitude=request.latitude,
            longitude=request.longitude,
            status="Available",
        )
        return self.repository.create_profile(profile)

    def get_my_profile(self, user):
        self._ensure_responder_role(user)
        profile = self.repository.get_profile_by_user_id(user.id)
        if profile is None:
            raise ResponderProfileNotFound()
        return profile

    def get_profile(self, responder_id: uuid.UUID):
        profile = self.repository.get_profile(responder_id)
        if profile is None:
            raise ResponderProfileNotFound()
        return profile

    def list_profiles(self):
        return self.repository.list_profiles()

    def update_status(self, user, status: str):
        self._ensure_responder_role(user)

        if status not in ALLOWED_RESPONDER_STATUSES:
            raise ValueError("Invalid responder status.")

        profile = self.repository.get_profile_by_user_id(user.id)
        if profile is None:
            raise ResponderProfileNotFound()

        if status in {"Available", "Offline"}:
            active_assignment = self.repository.get_active_assignment_for_responder(
                profile.id
            )
            if active_assignment is not None:
                raise ValueError(
                    f"Responder cannot become {status} while an active assignment exists."
                )

        profile.status = status
        self.repository.update_profile()
        return profile

    def update_location(self, user, latitude: float, longitude: float):
        self._ensure_responder_role(user)

        profile = self.repository.get_profile_by_user_id(user.id)
        if profile is None:
            raise ResponderProfileNotFound()

        profile.latitude = latitude
        profile.longitude = longitude

        location = ResponderLocation(
            responder_id=profile.id,
            latitude=latitude,
            longitude=longitude,
        )
        self.repository.update_profile()
        self.repository.create_location(location)
        return profile

    def create_assignment(self, user, request):
        self._ensure_responder_role(user)

        profile = self.repository.get_profile_by_user_id(user.id)
        if profile is None:
            raise ResponderProfileNotFound()

        emergency = self.repository.get_emergency_for_update(request.emergency_id)
        if emergency is None:
            raise EmergencyNotFound()

        active_assignment = self.repository.get_active_assignment_for_emergency(
            request.emergency_id
        )
        if active_assignment is not None:
            raise AssignmentAlreadyExists()

        existing = self.repository.get_assignment_for_emergency_and_responder(
            request.emergency_id,
            profile.id,
        )
        if existing:
            raise AssignmentAlreadyExists()

        if emergency.status not in {"Pending", "Accepted"}:
            raise ValueError(
                f"Cannot assign responder to emergency in status: {emergency.status}"
            )

        if profile.status != "Available":
            raise ValueError(
                f"Responder is not available for assignment: {profile.status}"
            )

        assignment = EmergencyAssignment(
            emergency_id=request.emergency_id,
            responder_id=profile.id,
            status="Assigned",
            distance_km=request.distance_km,
            eta_minutes=request.eta_minutes,
            notes=request.notes,
        )

        emergency.status = "Assigned"
        profile.status = "Busy"

        return self.repository.create_assignment(assignment)

    def get_assignment(self, user, assignment_id: uuid.UUID):
        self._ensure_responder_role(user)

        assignment = self.repository.get_assignment(assignment_id)
        if assignment is None:
            raise EmergencyAssignmentNotFound()

        profile = self.repository.get_profile_by_user_id(user.id)
        if profile is None or assignment.responder_id != profile.id:
            raise EmergencyAssignmentNotFound()

        return assignment

    def update_assignment(self, user, assignment_id: uuid.UUID, status: str, notes: str | None):
        self._ensure_responder_role(user)

        if status not in ALLOWED_ASSIGNMENT_STATUSES:
            raise ValueError("Invalid assignment status.")

        assignment = self.repository.get_assignment(assignment_id)
        if assignment is None:
            raise EmergencyAssignmentNotFound()

        profile = self.repository.get_profile_by_user_id(user.id)
        if profile is None or assignment.responder_id != profile.id:
            raise EmergencyAssignmentNotFound()

        previous_status = assignment.status
        if status != previous_status and status not in ALLOWED_ASSIGNMENT_TRANSITIONS.get(
            previous_status, set()
        ):
            raise ValueError(
                f"Invalid responder assignment status transition: "
                f"{previous_status} -> {status}"
            )

        emergency = self.repository.get_emergency(assignment.emergency_id)
        if emergency is None:
            raise EmergencyNotFound()

        expected_emergency_status = EMERGENCY_STATUS_BY_ASSIGNMENT.get(previous_status)
        if (
            expected_emergency_status is not None
            and emergency.status != expected_emergency_status
        ):
            raise ValueError(
                "Emergency status is out of sync with the responder assignment."
            )

        assignment.status = status
        if notes is not None:
            assignment.notes = notes

        emergency_status = EMERGENCY_STATUS_BY_ASSIGNMENT.get(status)
        if emergency_status is not None:
            emergency.status = emergency_status

        if status in {"Completed", "Cancelled"}:
            profile.status = "Available"

            # A dispatch reserves one hospital resource. Release that
            # reservation exactly once when the assignment reaches a
            # terminal state.
            if (
                previous_status not in {"Completed", "Cancelled"}
                and status in {"Completed", "Cancelled"}
            ):
                dispatch = self.repository.get_dispatch_by_assignment_id(
                    assignment.id
                )
                if dispatch is not None and dispatch.resource_id is not None:
                    resource = self.repository.get_hospital_resource(
                        dispatch.resource_id
                    )
                    if resource is not None:
                        resource.available_count = min(
                            resource.total_count,
                            resource.available_count + 1,
                        )
                        resource.is_available = resource.available_count > 0

        self.repository.update_profile()
        return assignment
