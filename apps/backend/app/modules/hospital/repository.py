import uuid

from sqlalchemy.orm import Session

from app.database.models.hospital import Hospital
from app.database.models.hospital_resource import HospitalResource


class HospitalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_hospital(self, hospital: Hospital):
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital

    def get_by_user_id(self, user_id: uuid.UUID):
        return self.db.query(Hospital).filter(Hospital.user_id == user_id).first()

    def get_by_id(self, hospital_id: uuid.UUID):
        return self.db.query(Hospital).filter(Hospital.id == hospital_id).first()

    def list_hospitals(self):
        return self.db.query(Hospital).filter(Hospital.is_active.is_(True)).order_by(Hospital.name.asc()).all()

    def create_resource(self, resource: HospitalResource):
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def get_resource(self, resource_id: uuid.UUID):
        return (
            self.db.query(HospitalResource)
            .filter(HospitalResource.id == resource_id)
            .with_for_update()
            .first()
        )

    def list_resources(self, hospital_id: uuid.UUID):
        return self.db.query(HospitalResource).filter(HospitalResource.hospital_id == hospital_id).order_by(HospitalResource.resource_type.asc()).all()

    def commit(self):
        self.db.commit()
