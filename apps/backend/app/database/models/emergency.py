import uuid

from sqlalchemy import ForeignKey, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class Emergency(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "emergencies"

    citizen_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    emergency_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        default="Medium",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Pending",
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    citizen = relationship(
        "User",
        back_populates="emergencies",
    )

    updates = relationship(
        "EmergencyUpdate",
        back_populates="emergency",
        cascade="all, delete-orphan",
    )

    assignments = relationship(
        "EmergencyAssignment",
        back_populates="emergency",
        cascade="all, delete-orphan",
    )
