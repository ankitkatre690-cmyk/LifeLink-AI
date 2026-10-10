import uuid

from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class EmergencyAssignment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "emergency_assignments"

    emergency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    responder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("responder_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), default="Assigned", nullable=False)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    eta_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    emergency = relationship("Emergency", back_populates="assignments")
    responder = relationship("ResponderProfile", back_populates="assignments")
    dispatch = relationship(
        "Dispatch",
        back_populates="assignment",
        uselist=False,
    )
