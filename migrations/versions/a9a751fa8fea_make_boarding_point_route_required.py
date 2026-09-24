"""make boarding point route required

Revision ID: a9a751fa8fea
Revises: 09b840196e3e
Create Date: 2026-09-24 19:57:07.821088

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a9a751fa8fea"
down_revision = "09b840196e3e"
branch_labels = None
depends_on = None


def upgrade():
    """
    Make route_id mandatory for boarding points.

    Existing boarding_points records were checked before this migration
    and there are currently no existing records, so making route_id
    NOT NULL is safe.

    No unrelated boarding_points columns are modified.
    network_events.event_id is intentionally preserved.
    """

    with op.batch_alter_table("boarding_points", schema=None) as batch_op:
        batch_op.alter_column(
            "route_id",
            existing_type=sa.VARCHAR(length=36),
            nullable=False
        )


def downgrade():
    """
    Allow route_id to be NULL again.
    """

    with op.batch_alter_table("boarding_points", schema=None) as batch_op:
        batch_op.alter_column(
            "route_id",
            existing_type=sa.VARCHAR(length=36),
            nullable=True
        )