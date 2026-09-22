import uuid

from sqlalchemy.orm import Session

from app.database.models.dispatch import Dispatch, DispatchLog
from app.database.models.emergency import Emergency
from app.database.models.emergency_assignment import EmergencyAssignment
from app.database.models.hospital import Hospital
from app.database.models.hospital_resource import HospitalResource
from app.database.models.responder_profile import ResponderProfile


class DispatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_emergency(self, emergency_id: uuid.UUID):
        return self.db.query(Emergency).filter(Emergency.id == emergency_id).first()

    def get_dispatch_for_emergency(self, emergency_id: uuid.UUID):
        return self.db.query(Dispatch).filter(
            Dispatch.emergency_id == emergency_id
        ).first()

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
            .order_by(
                HospitalResource.available_count.desc(),
                Hospital.name.asc(),
            )
            .with_for_update(of=HospitalResource)
            .first()
        )

    def create_assignment(self, assignment: EmergencyAssignment):
        self.db.add(assignment)
        self.db.flush()
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

    def get_logs(self, dispatch_id: uuid.UUID):
        return (
            self.db.query(DispatchLog)
            .filter(DispatchLog.dispatch_id == dispatch_id)
            .order_by(DispatchLog.created_at.asc())
            .all()
        )

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, entity):
        self.db.refresh(entity)
