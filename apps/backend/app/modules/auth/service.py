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
from app.modules.auth.schemas import RegisterRequest


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
            hashed_password=hash_password(
                request.password
            ),
            is_active=True,
        )

        return self.repository.create_user(user)

    # ---------------------------------
    # LOGIN
    # ---------------------------------

    def login(
        self,
        email: str,
        password: str,
    ):

        user = self.repository.get_user_by_email(
            email
        )

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        access_token = create_access_token(
            subject=str(user.id)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }