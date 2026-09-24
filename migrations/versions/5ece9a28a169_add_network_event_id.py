"""add network event id

Revision ID: 5ece9a28a169
Revises: b9a096f9cb79
Create Date: 2026-09-23 19:53:57.372108

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ece9a28a169"
down_revision = "b9a096f9cb79"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("network_events", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "event_id",
                sa.String(length=100),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            "uq_network_events_event_id",
            ["event_id"]
        )


def downgrade():
    with op.batch_alter_table("network_events", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_network_events_event_id",
            type_="unique"
        )

        batch_op.drop_column("event_id")