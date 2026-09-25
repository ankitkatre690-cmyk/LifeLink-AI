import uuid

from app.database.models.dispatch import Dispatch, DispatchLog
from app.database.models.emergency_assignment import EmergencyAssignment
from app.modules.dispatch.exceptions import (
    DispatchAlreadyExists,
    DispatchNotFound,
    EmergencyNotFound,
    NoAvailableHospitalResource,
    NoAvailableResponder,
)
from app.modules.dispatch.repository import DispatchRepository
from app.modules.dispatch.state import validate_dispatch_transition
from app.modules.dispatch.utils import estimate_eta_minutes, haversine_distance_km


FINAL_DISPATCH_STATUSES = {"Completed", "Cancelled"}


class DispatchService:
    def __init__(self, repository: DispatchRepository):
        self.repository = repository

    def dispatch_emergency(self, emergency_id: uuid.UUID):
        emergency = self.repository.get_emergency_for_update(emergency_id)
        if emergency is None:
            raise EmergencyNotFound()

        if emergency.status in {"Completed", "Cancelled"}:
            raise ValueError(f"Cannot dispatch a terminal emergency: {emergency.status}")
        if self.repository.get_dispatch_for_emergency(emergency_id):
            raise DispatchAlreadyExists()
        if self.repository.get_active_assignment_for_emergency(emergency_id):
            raise DispatchAlreadyExists()

        responders = self.repository.get_available_responders()
        if not responders:
            raise NoAvailableResponder()
        distance_km, responder = min(
            (
                (
                    haversine_distance_km(
                        emergency.latitude,
                        emergency.longitude,
                        responder.latitude,
                        responder.longitude,
                    ),
                    responder,
                )
                for responder in responders
            ),
            key=lambda item: item[0],
        )
        eta_minutes = estimate_eta_minutes(distance_km)
        hospital_result = self.repository.get_available_hospital_resource()
        if hospital_result is None:
            raise NoAvailableHospitalResource()
        resource, hospital = hospital_result

        try:
            assignment = EmergencyAssignment(
                emergency_id=emergency.id,
                responder_id=responder.id,
                status="Assigned",
                distance_km=round(distance_km, 3),
                eta_minutes=eta_minutes,
                notes="Automatically assigned by dispatch engine.",
            )
            self.repository.create_assignment(assignment)
            responder.status = "Busy"
            emergency.status = "Assigned"
            if resource.available_count <= 0:
                raise NoAvailableHospitalResource()
            resource.available_count -= 1
            resource.is_available = resource.available_count > 0

            dispatch = Dispatch(
                emergency_id=emergency.id,
                assignment_id=assignment.id,
                hospital_id=hospital.id,
                resource_id=resource.id,
                distance_km=round(distance_km, 3),
                eta_minutes=eta_minutes,
                dispatch_status="Assigned",
            )
            self.repository.create_dispatch(dispatch)
            self.repository.create_log(
                DispatchLog(
                    dispatch_id=dispatch.id,
                    status="Assigned",
                    message=(
                        f"Responder {responder.id} assigned at {round(distance_km, 3)} km; "
                        f"ETA {eta_minutes} minutes. Hospital {hospital.id} resource reserved."
                    ),
                )
            )
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

        self.repository.refresh(dispatch)
        return dispatch

    def get_dispatch(self, dispatch_id: uuid.UUID):
        dispatch = self.repository.get_dispatch(dispatch_id)
        if dispatch is None:
            raise DispatchNotFound()
        return dispatch

    def get_dispatch_for_user(self, dispatch_id: uuid.UUID, user_id: uuid.UUID, role: str | None):
        dispatch = self.get_dispatch(dispatch_id)
        if not self.repository.user_can_view_dispatch(dispatch_id, user_id, role):
            raise PermissionError("You are not authorized to view this dispatch.")
        return dispatch

    def get_logs_for_user(self, dispatch_id: uuid.UUID, user_id: uuid.UUID, role: str | None):
        self.get_dispatch_for_user(dispatch_id, user_id, role)
        return self.repository.get_logs(dispatch_id)

    def update_dispatch_status(self, dispatch_id: uuid.UUID, status: str):
        dispatch = self.get_dispatch(dispatch_id)
        previous_status = dispatch.dispatch_status
        if status == previous_status:
            return dispatch
        validate_dispatch_transition(previous_status, status)

        assignment = self.repository.get_assignment(dispatch.assignment_id)
        if assignment is None:
            raise ValueError("Dispatch assignment is missing.")
        emergency = self.repository.get_emergency_for_update(dispatch.emergency_id)
        if emergency is None:
            raise EmergencyNotFound()
        assignment.status = status
        dispatch.dispatch_status = status
        emergency.status = status
        if status in FINAL_DISPATCH_STATUSES and dispatch.resource_id is not None:
            resource = self.repository.get_hospital_resource(dispatch.resource_id)
            if resource is not None:
                resource.available_count = min(resource.total_count, resource.available_count + 1)
                resource.is_available = resource.available_count > 0
        self.repository.create_log(DispatchLog(dispatch_id=dispatch.id, status=status))
        self.repository.commit()
        self.repository.refresh(dispatch)
        return dispatch
