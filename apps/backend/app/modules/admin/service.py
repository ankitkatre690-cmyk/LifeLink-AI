import uuid

from app.modules.admin.exceptions import AdminUserNotFound
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import AdminUserStatusUpdate


class AdminService:
    def __init__(self, repository: AdminRepository):
        self.repository = repository

    def dashboard(self):
        return self.repository.dashboard_counts()

    def list_users(self, limit: int, offset: int):
        return self.repository.list_users(limit, offset)

    def update_user_status(self, user_id: uuid.UUID, request: AdminUserStatusUpdate):
        user = self.repository.get_user(user_id)
        if user is None:
            raise AdminUserNotFound()

        user.is_active = request.is_active
        self.repository.commit()
        self.repository.refresh(user)
        return user
