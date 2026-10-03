import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class Dispatch(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dispatches"
    __table_args__ = (
        CheckConstraint(
            "dispatch_status IN ('Assigned', 'Accepted', 'EnRoute', 'OnScene', 'Completed', 'Cancelled')",
            name="ck_dispatches_dispatch_status_valid",
        ),
    )

    emergency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergencies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergency_assignments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    hospital_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospital_resources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    eta_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    dispatch_status: Mapped[str] = mapped_column(
        String(30),
        default="Assigned",
        nullable=False,
    )

    emergency = relationship("Emergency", back_populates="dispatches")
    assignment = relationship("EmergencyAssignment", back_populates="dispatch")
    hospital = relationship("Hospital", back_populates="dispatches")
    resource = relationship("HospitalResource")
    logs = relationship(
        "DispatchLog",
        back_populates="dispatch",
        cascade="all, delete-orphan",
    )


class DispatchLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "dispatch_logs"

    dispatch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    dispatch = relationship("Dispatch", back_populates="logs")
