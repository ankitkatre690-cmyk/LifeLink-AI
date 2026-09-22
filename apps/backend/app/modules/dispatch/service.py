import uuid

from app.database.models.dispatch import Dispatch, DispatchLog
from app.database.models.emergency_assignment import EmergencyAssignment
from app.modules.dispatch.exceptions import (
    DispatchAlreadyExists,
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
        emergency = self.repository.get_emergency(emergency_id)
        if emergency is None:
            raise EmergencyNotFound()

        if self.repository.get_dispatch_for_emergency(emergency_id):
            raise DispatchAlreadyExists()

        responders = self.repository.get_available_responders()
        if not responders:
            raise NoAvailableResponder()

        ranked = []
        for responder in responders:
            distance = haversine_distance_km(
                emergency.latitude,
                emergency.longitude,
                responder.latitude,
                responder.longitude,
            )
            ranked.append((distance, responder))

        distance_km, responder = min(ranked, key=lambda item: item[0])
        eta_minutes = estimate_eta_minutes(distance_km)

        hospital_result = self.repository.get_available_hospital_resource()
        if hospital_result is None:
            raise NoAvailableHospitalResource()

        _, hospital = hospital_result

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

        dispatch = Dispatch(
            emergency_id=emergency.id,
            assignment_id=assignment.id,
            hospital_id=hospital.id,
            distance_km=round(distance_km, 3),
            eta_minutes=eta_minutes,
            dispatch_status="Assigned",
        )
        self.repository.create_dispatch(dispatch)

        log = DispatchLog(
            dispatch_id=dispatch.id,
            status="Assigned",
            message=(
                f"Responder {responder.id} assigned at "
                f"{round(distance_km, 3)} km; ETA {eta_minutes} minutes. "
                f"Hospital {hospital.id} selected based on available resources."
            ),
        )
        self.repository.create_log(log)

        self.repository.commit()
        self.repository.refresh(dispatch)
        return dispatch

    def get_dispatch(self, dispatch_id: uuid.UUID):
        dispatch = self.repository.db.query(Dispatch).filter(
            Dispatch.id == dispatch_id
        ).first()
        if dispatch is None:
            raise EmergencyNotFound()
        return dispatch

    def get_logs(self, dispatch_id: uuid.UUID):
        return (
            self.repository.db.query(DispatchLog)
            .filter(DispatchLog.dispatch_id == dispatch_id)
            .order_by(DispatchLog.created_at.asc())
            .all()
        )
