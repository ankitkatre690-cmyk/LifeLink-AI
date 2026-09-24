from uuid import UUID

from app.database.models.hospital import Hospital
from app.database.models.hospital_resource import HospitalResource
from app.modules.hospital.exceptions import (
    HospitalProfileAlreadyExists,
    HospitalProfileNotFound,
    HospitalResourceNotFound,
    InvalidHospitalRole,
    InvalidResourceCount,
)
from app.modules.hospital.repository import HospitalRepository


class HospitalService:
    def __init__(self, repository: HospitalRepository):
        self.repository = repository

    @staticmethod
    def _ensure_hospital_role(user):
        if user.role is None or user.role.name != "Hospital":
            raise InvalidHospitalRole()

    def create_profile(self, user, request):
        self._ensure_hospital_role(user)
        if self.repository.get_by_user_id(user.id):
            raise HospitalProfileAlreadyExists()
        hospital = Hospital(user_id=user.id, name=request.name, address=request.address, phone=request.phone, is_active=True)
        return self.repository.create_hospital(hospital)

    def get_my_profile(self, user):
        self._ensure_hospital_role(user)
        hospital = self.repository.get_by_user_id(user.id)
        if hospital is None:
            raise HospitalProfileNotFound()
        return hospital

    def get_profile(self, hospital_id: UUID):
        hospital = self.repository.get_by_id(hospital_id)
        if hospital is None or not hospital.is_active:
            raise HospitalProfileNotFound()
        return hospital

    def list_hospitals(self):
        return self.repository.list_hospitals()

    def add_resource(self, user, request):
        self._ensure_hospital_role(user)
        hospital = self.repository.get_by_user_id(user.id)
        if hospital is None:
            raise HospitalProfileNotFound()
        if request.available_count > request.total_count:
            raise InvalidResourceCount()
        resource = HospitalResource(hospital_id=hospital.id, resource_type=request.resource_type, total_count=request.total_count, available_count=request.available_count, is_available=request.available_count > 0)
        return self.repository.create_resource(resource)

    def list_resources(self, hospital_id: UUID):
        hospital = self.repository.get_by_id(hospital_id)
        if hospital is None or not hospital.is_active:
            raise HospitalProfileNotFound()
        return self.repository.list_resources(hospital_id)

    def update_resource(self, user, resource_id: UUID, request):
        self._ensure_hospital_role(user)
        hospital = self.repository.get_by_user_id(user.id)
        if hospital is None:
            raise HospitalProfileNotFound()
        resource = self.repository.get_resource(resource_id)
        if resource is None or resource.hospital_id != hospital.id:
            raise HospitalResourceNotFound()
        if request.available_count > request.total_count:
            raise InvalidResourceCount()
        if request.total_count < 0 or request.available_count < 0:
            raise InvalidResourceCount()
        resource.total_count = request.total_count
        resource.available_count = request.available_count
        resource.is_available = request.is_available and request.available_count > 0
        self.repository.commit()
        return resource
