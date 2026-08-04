import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class EmergencyUpdate(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "emergency_updates"

    emergency_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("emergencies.id", ondelete="CASCADE"),
        nullable=False,
    )

    updated_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    remarks: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    # -----------------------
    # Relationships
    # -----------------------

    emergency = relationship(
        "Emergency",
        back_populates="updates",
    )

    user = relationship("User")