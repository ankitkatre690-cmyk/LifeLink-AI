from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.modules.admin.exceptions import AdminUserNotFound
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    AdminDashboardResponse,
    AdminUserResponse,
    AdminUserStatusUpdate,
)
from app.modules.admin.service import AdminService
from app.modules.auth.dependencies import get_current_user


router = APIRouter(prefix="/admin", tags=["Admin"])


def _service(db: Session) -> AdminService:
    return AdminService(AdminRepository(db))


def _ensure_admin(user: User):
    if user.role is None or user.role.name != "Admin":
        raise HTTPException(403, "Only Admin users can access admin operations.")


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    return _service(db).dashboard()


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    return _service(db).list_users(limit, offset)


@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
def update_user_status(
    user_id: UUID,
    request: AdminUserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    if user_id == current_user.id and request.is_active is False:
        raise HTTPException(400, "An admin cannot deactivate their own account.")

    try:
        return _service(db).update_user_status(user_id, request)
    except AdminUserNotFound:
        raise HTTPException(404, "User not found.")
