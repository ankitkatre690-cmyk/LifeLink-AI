from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.citizen.exceptions import (
    CitizenProfileExists,
    CitizenProfileNotFound,
)
from app.modules.citizen.repository import CitizenRepository
from app.modules.citizen.schemas import (
    CitizenProfileCreate,
    CitizenProfileResponse,
)
from app.modules.citizen.service import CitizenService

router = APIRouter(
    prefix="/citizen",
    tags=["Citizen"],
)


@router.post(
    "/profile",
    response_model=CitizenProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    request: CitizenProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CitizenService(CitizenRepository(db))

    try:
        return service.create_profile(
            current_user.id,
            request,
        )

    except CitizenProfileExists:
        raise HTTPException(
            status_code=400,
            detail="Citizen profile already exists.",
        )


@router.get(
    "/profile",
    response_model=CitizenProfileResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CitizenService(CitizenRepository(db))

    try:
        return service.get_profile(current_user.id)

    except CitizenProfileNotFound:
        raise HTTPException(
            status_code=404,
            detail="Citizen profile not found.",
        )


@router.put(
    "/profile",
    response_model=CitizenProfileResponse,
)
def update_profile(
    request: CitizenProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CitizenService(CitizenRepository(db))

    try:
        return service.update_profile(
            current_user.id,
            request,
        )

    except CitizenProfileNotFound:
        raise HTTPException(
            status_code=404,
            detail="Citizen profile not found.",
        )


@router.delete(
    "/profile",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CitizenService(CitizenRepository(db))

    try:
        service.delete_profile(current_user.id)
        return

    except CitizenProfileNotFound:
        raise HTTPException(
            status_code=404,
            detail="Citizen profile not found.",
        )