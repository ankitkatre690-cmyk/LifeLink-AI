"""enforce dispatch and assignment lifecycle consistency

Revision ID: f1a2b3c4d5e6
Revises: a7b9c2d4e6f8
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "a7b9c2d4e6f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_ALLOWED_STATUSES = "('Assigned', 'Accepted', 'EnRoute', 'OnScene', 'Completed', 'Cancelled')"


def upgrade() -> None:
    op.create_check_constraint(
        "ck_dispatches_dispatch_status_valid",
        "dispatches",
        f"dispatch_status IN {_ALLOWED_STATUSES}",
    )

    op.execute(
        """
        CREATE FUNCTION validate_dispatch_assignment_status()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            assignment_status text;
            dispatch_status text;
        BEGIN
            IF TG_TABLE_NAME = 'dispatches' THEN
                SELECT status INTO assignment_status
                FROM emergency_assignments
                WHERE id = NEW.assignment_id;

                IF assignment_status IS NOT NULL
                   AND NEW.dispatch_status <> assignment_status THEN
                    RAISE EXCEPTION
                        'Dispatch % status % must match assignment % status %',
                        NEW.id, NEW.dispatch_status,
                        NEW.assignment_id, assignment_status;
                END IF;
            ELSE
                SELECT d.dispatch_status INTO dispatch_status
                FROM dispatches AS d
                WHERE d.assignment_id = NEW.id;

                IF dispatch_status IS NOT NULL
                   AND dispatch_status <> NEW.status THEN
                    RAISE EXCEPTION
                        'Assignment % status % must match dispatch status %',
                        NEW.id, NEW.status, dispatch_status;
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER dispatch_assignment_status_consistency
        AFTER INSERT OR UPDATE OF assignment_id, dispatch_status
        ON dispatches
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION validate_dispatch_assignment_status();
        """
    )

    op.execute(
        """
        CREATE CONSTRAINT TRIGGER assignment_dispatch_status_consistency
        AFTER INSERT OR UPDATE OF status
        ON emergency_assignments
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION validate_dispatch_assignment_status();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS assignment_dispatch_status_consistency ON emergency_assignments"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS dispatch_assignment_status_consistency ON dispatches"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_dispatch_assignment_status()")
    op.drop_constraint(
        "ck_dispatches_dispatch_status_valid",
        "dispatches",
        type_="check",
    )
