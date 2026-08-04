from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models.role import Role
from app.database.models.user import User


class AuthRepository:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # USER
    # -------------------------

    def get_user_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # -------------------------
    # ROLE
    # -------------------------

    def get_role_by_name(self, role: str):
        return (
            self.db.query(Role)
            .filter(Role.name == role)
            .first()
        )

    # -------------------------
    # LOGIN
    # -------------------------

    def update_last_login(self, user: User):

        user.last_login = datetime.now(timezone.utc)

        self.db.commit()

        self.db.refresh(user)

        return user