from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.family.exceptions import (
    FamilyAlreadyExists,
    FamilyMemberAlreadyExists,
    FamilyMemberNotFound,
    FamilyNotFound,
)
from app.modules.family.repository import FamilyRepository
from app.modules.family.schemas import (
    FamilyCreate,
    FamilyMemberCreate,
    FamilyMemberResponse,
    FamilyResponse,
)
from app.modules.family.service import FamilyService

router = APIRouter(
    prefix="/family",
    tags=["Family"],
)


# ---------------------------------------
# Create Family
# ---------------------------------------

@router.post(
    "",
    response_model=FamilyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_family(
    request: FamilyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = FamilyService(FamilyRepository(db))

    try:
        return service.create_family(
            current_user.id,
            request,
        )

    except FamilyAlreadyExists:
        raise HTTPException(
            status_code=400,
            detail="Family already exists.",
        )


# ---------------------------------------
# Get Family
# ---------------------------------------

@router.get(
    "",
    response_model=FamilyResponse,
)
def get_family(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = FamilyService(FamilyRepository(db))

    try:
        return service.get_family(current_user.id)

    except FamilyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Family not found.",
        )


# ---------------------------------------
# Delete Family
# ---------------------------------------

@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_family(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = FamilyService(FamilyRepository(db))

    try:
        service.delete_family(current_user.id)

    except FamilyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Family not found.",
        )


# ---------------------------------------
# Add Family Member
# ---------------------------------------

@router.post(
    "/member",
    response_model=FamilyMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    request: FamilyMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = FamilyService(FamilyRepository(db))

    try:
        return service.add_member(
            current_user.id,
            request,
        )

    except FamilyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Family not found.",
        )

    except FamilyMemberAlreadyExists:
        raise HTTPException(
            status_code=400,
            detail="Member already exists.",
        )


# ---------------------------------------
# Get Members
# ---------------------------------------

@router.get(
    "/members",
    response_model=list[FamilyMemberResponse],
)
def get_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = FamilyService(FamilyRepository(db))

    try:
        return service.get_members(current_user.id)

    except FamilyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Family not found.",
        )


# ---------------------------------------
# Remove Member
# ---------------------------------------

@router.delete(
    "/member/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = FamilyService(FamilyRepository(db))

    try:
        service.remove_member(
            current_user.id,
            user_id,
        )

    except FamilyNotFound:
        raise HTTPException(
            status_code=404,
            detail="Family not found.",
        )

    except FamilyMemberNotFound:
        raise HTTPException(
            status_code=404,
            detail="Member not found.",
        )