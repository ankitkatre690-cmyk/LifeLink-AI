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
from app.modules.dispatch.utils import estimate_eta_minutes, haversine_distance_km


class DispatchService:
    def __init__(self, repository: DispatchRepository):
        self.repository = repository

    def dispatch_emergency(self, emergency_id: uuid.UUID):
        emergency = self.repository.get_emergency_for_update(emergency_id)
        if emergency is None:
            raise EmergencyNotFound()

        if emergency.status in {"Completed", "Cancelled"}:
            raise ValueError(
                f"Cannot dispatch a terminal emergency: {emergency.status}"
            )

        if self.repository.get_dispatch_for_emergency(emergency_id):
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
                        f"Responder {responder.id} assigned at "
                        f"{round(distance_km, 3)} km; ETA {eta_minutes} minutes. "
                        f"Hospital {hospital.id} resource reserved."
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

    def get_dispatch_for_user(
        self,
        dispatch_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str | None,
    ):
        dispatch = self.repository.get_dispatch(dispatch_id)
        if dispatch is None:
            raise DispatchNotFound()

        if not self.repository.user_can_view_dispatch(
            dispatch_id,
            user_id,
            role,
        ):
            raise PermissionError("You are not authorized to view this dispatch.")

        return dispatch

    def get_logs_for_user(
        self,
        dispatch_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str | None,
    ):
        self.get_dispatch_for_user(dispatch_id, user_id, role)
        return self.repository.get_logs(dispatch_id)
