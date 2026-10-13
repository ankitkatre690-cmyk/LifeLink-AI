import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class PoliceCase(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "police_cases"

    emergency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergencies.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    police_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_status: Mapped[str] = mapped_column(
        String(30), default="Open", nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    emergency = relationship("Emergency", back_populates="police_case")
    police_user = relationship("User")
