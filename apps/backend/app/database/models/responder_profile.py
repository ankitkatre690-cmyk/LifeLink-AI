import uuid

from sqlalchemy import ForeignKey, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class ResponderProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "responder_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    responder_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Available",
        nullable=False,
    )

    vehicle_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="responder_profile",
    )

    locations = relationship(
        "ResponderLocation",
        back_populates="responder",
        cascade="all, delete-orphan",
    )

    assignments = relationship(
        "EmergencyAssignment",
        back_populates="responder",
        cascade="all, delete-orphan",
    )
