from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database.session import get_db
from app.database.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRoleError,
)
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ---------------- REGISTER ----------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(AuthRepository(db))

    try:
        return service.register(request)

    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    except InvalidRoleError:
        raise HTTPException(
            status_code=400,
            detail="Invalid role.",
        )


# ---------------- LOGIN ----------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    service = AuthService(AuthRepository(db))

    try:
        return service.login(
            form_data.username,
            form_data.password,
        )

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )


# ---------------- CURRENT USER ----------------

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user