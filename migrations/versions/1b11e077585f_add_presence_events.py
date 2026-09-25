"""add presence events

Revision ID: 1b11e077585f
Revises: 5ece9a28a169
Create Date: 2026-09-23 20:03:07.409055

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "1b11e077585f"
down_revision = "5ece9a28a169"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("presence_events", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "event_id",
                sa.String(length=100),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "rssi",
                sa.Float(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "source",
                sa.String(length=40),
                nullable=False,
                server_default="DRIVER"
            )
        )

        batch_op.alter_column(
            "event_type",
            existing_type=sa.VARCHAR(length=30),
            nullable=False
        )

        batch_op.alter_column(
            "detected_at",
            existing_type=postgresql.TIMESTAMP(),
            nullable=False
        )

        batch_op.create_unique_constraint(
            "uq_presence_events_event_id",
            ["event_id"]
        )

        batch_op.drop_column("detected")
        batch_op.drop_column("signal_strength")
        batch_op.drop_column("ble_device_id")


def downgrade():

    with op.batch_alter_table("presence_events", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "ble_device_id",
                sa.VARCHAR(length=100),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "signal_strength",
                sa.INTEGER(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "detected",
                sa.BOOLEAN(),
                nullable=False
            )
        )

        batch_op.drop_constraint(
            "uq_presence_events_event_id",
            type_="unique"
        )

        batch_op.alter_column(
            "detected_at",
            existing_type=postgresql.TIMESTAMP(),
            nullable=True
        )

        batch_op.alter_column(
            "event_type",
            existing_type=sa.VARCHAR(length=30),
            nullable=True
        )

        batch_op.drop_column("source")
        batch_op.drop_column("rssi")
        batch_op.drop_column("event_id")