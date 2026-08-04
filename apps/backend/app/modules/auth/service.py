from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.models.user import User
from app.modules.auth.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRoleError,
)
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
)


class AuthService:

    def __init__(self, repository: AuthRepository):
        self.repository = repository

    # ---------------------------------
    # REGISTER
    # ---------------------------------

    def register(self, request: RegisterRequest):

        existing_user = self.repository.get_user_by_email(
            request.email
        )

        if existing_user:
            raise EmailAlreadyExistsError()

        role = self.repository.get_role_by_name(
            request.role
        )

        if role is None:
            raise InvalidRoleError()

        user = User(
            role_id=role.id,
            email=request.email,
            phone=request.phone,
            password_hash=hash_password(request.password),
            is_active=True,
            is_verified=False,
        )

        return self.repository.create_user(user)

    # ---------------------------------
    # LOGIN
    # ---------------------------------

    def login(self, request: LoginRequest):

        user = self.repository.get_user_by_email(
            request.email
        )

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        self.repository.update_last_login(user)

        token = create_access_token(user.id)

        return {
            "access_token": token,
            "token_type": "bearer",
        }