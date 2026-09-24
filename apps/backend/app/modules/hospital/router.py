from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.hospital.exceptions import HospitalProfileAlreadyExists, HospitalProfileNotFound, HospitalResourceNotFound, InvalidHospitalRole, InvalidResourceCount
from app.modules.hospital.repository import HospitalRepository
from app.modules.hospital.schemas import HospitalCreate, HospitalResponse, ResourceCreate, ResourceResponse, ResourceUpdate
from app.modules.hospital.service import HospitalService

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


def _service(db: Session) -> HospitalService:
    return HospitalService(HospitalRepository(db))


@router.post("", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def create_hospital_profile(request: HospitalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return _service(db).create_profile(current_user, request)
    except InvalidHospitalRole:
        raise HTTPException(403, "Current user does not have Hospital role.")
    except HospitalProfileAlreadyExists:
        raise HTTPException(409, "Hospital profile already exists.")


@router.get("/me", response_model=HospitalResponse)
def get_my_hospital_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return _service(db).get_my_profile(current_user)
    except InvalidHospitalRole:
        raise HTTPException(403, "Current user does not have Hospital role.")
    except HospitalProfileNotFound:
        raise HTTPException(404, "Hospital profile not found.")


@router.get("", response_model=list[HospitalResponse])
def list_hospitals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _service(db).list_hospitals()


@router.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def add_resource(request: ResourceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return _service(db).add_resource(current_user, request)
    except InvalidHospitalRole:
        raise HTTPException(403, "Current user does not have Hospital role.")
    except HospitalProfileNotFound:
        raise HTTPException(404, "Hospital profile not found.")
    except InvalidResourceCount:
        raise HTTPException(400, "Available count cannot exceed total count.")


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(hospital_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return _service(db).get_profile(hospital_id)
    except HospitalProfileNotFound:
        raise HTTPException(404, "Hospital not found.")


@router.get("/{hospital_id}/resources", response_model=list[ResourceResponse])
def list_resources(hospital_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return _service(db).list_resources(hospital_id)
    except HospitalProfileNotFound:
        raise HTTPException(404, "Hospital not found.")


@router.patch("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: UUID, request: ResourceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return _service(db).update_resource(current_user, resource_id, request)
    except InvalidHospitalRole:
        raise HTTPException(403, "Current user does not have Hospital role.")
    except HospitalProfileNotFound:
        raise HTTPException(404, "Hospital profile not found.")
    except HospitalResourceNotFound:
        raise HTTPException(404, "Hospital resource not found.")
    except InvalidResourceCount:
        raise HTTPException(400, "Available count cannot exceed total count.")
