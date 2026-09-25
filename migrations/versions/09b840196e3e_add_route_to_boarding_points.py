"""add route to boarding points

Revision ID: 09b840196e3e
Revises: add_student_bus_ble
Create Date: 2026-09-24 19:44:50.255798

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "09b840196e3e"
down_revision = "add_student_bus_ble"
branch_labels = None
depends_on = None


def upgrade():
    """
    Add route_id to boarding_points.

    The column is initially nullable because existing boarding points
    may already exist in the database and we do not yet know which
    route each existing boarding point belongs to.

    The network_events.event_id column is intentionally preserved
    because it is required for event idempotency/offline sync.
    """

    with op.batch_alter_table("boarding_points", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "route_id",
                sa.String(length=36),
                nullable=True
            )
        )

        batch_op.create_foreign_key(
            "fk_boarding_points_route_id",
            "routes",
            ["route_id"],
            ["id"]
        )


def downgrade():
    """
    Remove route_id from boarding_points.
    """

    with op.batch_alter_table("boarding_points", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_boarding_points_route_id",
            type_="foreignkey"
        )

        batch_op.drop_column("route_id")