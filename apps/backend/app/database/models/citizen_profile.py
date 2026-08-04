import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin, UUIDMixin


class CitizenProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "citizen_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    blood_group: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    profile_photo: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    pincode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    emergency_contact_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    emergency_contact_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    allergies: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    medical_conditions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    medications: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organ_donor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    height: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    weight: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="citizen_profile",
    )