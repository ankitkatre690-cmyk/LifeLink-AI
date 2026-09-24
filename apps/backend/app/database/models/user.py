import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    role = relationship("Role", back_populates="users")
    citizen_profile = relationship("CitizenProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    family_groups = relationship("FamilyGroup", foreign_keys="FamilyGroup.created_by", back_populates="creator")
    family_memberships = relationship("FamilyMember", foreign_keys="FamilyMember.user_id", back_populates="user")
    emergencies = relationship("Emergency", back_populates="citizen", cascade="all, delete-orphan")
    responder_profile = relationship("ResponderProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    hospital_profile = relationship("Hospital", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
    women_safety_profile = relationship(
        "WomenSafetyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
