import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import TimestampMixin, UUIDMixin


class FamilyMember(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "family_members"

    family_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("family_groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Avoid naming this field "relationship"
    # because it conflicts with SQLAlchemy's relationship() function.
    relationship_type: Mapped[str] = mapped_column(
        "relationship",
        String(50),
        nullable=False,
    )

    is_guardian: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -------------------------
    # Relationships
    # -------------------------

    family_group = relationship(
        "FamilyGroup",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="family_memberships",
    )