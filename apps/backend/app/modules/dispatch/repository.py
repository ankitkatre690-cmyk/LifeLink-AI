import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models.dispatch import Dispatch, DispatchLog
from app.database.models.emergency import Emergency
from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.hospital import Hospital
from app.database.models.hospital_resource import HospitalResource
from app.database.models.responder_profile import ResponderProfile
from app.modules.dispatch.exceptions import DispatchAlreadyExists


class DispatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_emergency(self, emergency_id: uuid.UUID):
        return self.db.query(Emergency).filter(Emergency.id == emergency_id).first()

    def get_emergency_for_update(self, emergency_id: uuid.UUID):
        return self.db.query(Emergency).filter(Emergency.id == emergency_id).with_for_update().first()

    def get_dispatch_for_emergency(self, emergency_id: uuid.UUID):
        return self.db.query(Dispatch).filter(Dispatch.emergency_id == emergency_id).first()

    def get_active_assignment_for_emergency(self, emergency_id: uuid.UUID):
        return (
            self.db.query(EmergencyAssignment)
            .filter(
                EmergencyAssignment.emergency_id == emergency_id,
                EmergencyAssignment.status.in_(["Assigned", "Accepted", "EnRoute", "OnScene"]),
            )
            .first()
        )

    def get_available_responders(self):
        return (
            self.db.query(ResponderProfile)
            .filter(
                ResponderProfile.status == "Available",
                ResponderProfile.latitude.is_not(None),
                ResponderProfile.longitude.is_not(None),
            )
            .with_for_update()
            .all()
        )

    def get_available_hospital_resource(self):
        return (
            self.db.query(HospitalResource, Hospital)
            .join(Hospital, Hospital.id == HospitalResource.hospital_id)
            .filter(
                Hospital.is_active.is_(True),
                HospitalResource.available_count > 0,
                HospitalResource.is_available.is_(True),
            )
            .order_by(HospitalResource.available_count.desc(), Hospital.name.asc())
            .with_for_update(of=HospitalResource)
            .first()
        )

    def create_assignment(self, assignment: EmergencyAssignment):
        self.db.add(assignment)
        try:
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            if "uq_emergency_assignments_active_emergency" in str(exc.orig):
                raise DispatchAlreadyExists() from exc
            raise
        return assignment

    def create_dispatch(self, dispatch: Dispatch):
        self.db.add(dispatch)
        self.db.flush()
        return dispatch

    def create_log(self, log: DispatchLog):
        self.db.add(log)
        self.db.flush()
        return log

    def get_dispatch(self, dispatch_id: uuid.UUID):
        return self.db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()

    def get_assignment(self, assignment_id: uuid.UUID):
        return self.db.query(EmergencyAssignment).filter(EmergencyAssignment.id == assignment_id).first()

    def get_hospital_resource(self, resource_id: uuid.UUID):
        return self.db.query(HospitalResource).filter(HospitalResource.id == resource_id).with_for_update().first()

    def user_can_view_dispatch(self, dispatch_id: uuid.UUID, user_id: uuid.UUID, role: str | None):
        if role in {"Police", "Admin"}:
            return True
        query = (
            self.db.query(Dispatch.id)
            .outerjoin(EmergencyAssignment, Dispatch.assignment_id == EmergencyAssignment.id)
            .outerjoin(ResponderProfile, EmergencyAssignment.responder_id == ResponderProfile.id)
            .outerjoin(Hospital, Dispatch.hospital_id == Hospital.id)
            .filter(Dispatch.id == dispatch_id)
        )
        if role == "Responder":
            return query.filter(ResponderProfile.user_id == user_id).first() is not None
        if role == "Hospital":
            return query.filter(Hospital.user_id == user_id).first() is not None
        return False

    def get_logs(self, dispatch_id: uuid.UUID):
        return self.db.query(DispatchLog).filter(DispatchLog.dispatch_id == dispatch_id).order_by(DispatchLog.created_at.asc()).all()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, entity):
        self.db.refresh(entity)
