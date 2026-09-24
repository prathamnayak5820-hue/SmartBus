"""reconcile network events schema

Revision ID: reconcile_network_events
Revises: 0a9952a23586
"""

from alembic import op
import sqlalchemy as sa


revision = "reconcile_network_events"
down_revision = "0a9952a23586"
branch_labels = None
depends_on = None


def upgrade():
    # Add the new columns first.
    op.add_column(
        "network_events",
        sa.Column("status", sa.String(length=20), nullable=True)
    )

    op.add_column(
        "network_events",
        sa.Column("recorded_at", sa.DateTime(), nullable=True)
    )

    # Preserve existing data.
    op.execute(
        """
        UPDATE network_events
        SET status = COALESCE(network_status, 'UNKNOWN'),
            recorded_at = COALESCE(created_at, CURRENT_TIMESTAMP)
        """
    )

    # Make the new columns required.
    op.alter_column(
        "network_events",
        "status",
        existing_type=sa.String(length=20),
        nullable=False
    )

    op.alter_column(
        "network_events",
        "recorded_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    # Remove obsolete columns.
    op.drop_column("network_events", "source")
    op.drop_column("network_events", "network_status")
    op.drop_column("network_events", "signal_strength")
    op.drop_column("network_events", "message")
    op.drop_column("network_events", "created_at")


def downgrade():
    # Restore the old columns.
    op.add_column(
        "network_events",
sa.Column("source", sa.String(length=40), nullable=False, server_default="DRIVER")
    )

    op.add_column(
        "network_events",
        sa.Column(
    "network_status",
    sa.String(length=30),
    nullable=False,
    server_default="UNKNOWN"
)
    )

    op.add_column(
        "network_events",
        sa.Column("signal_strength", sa.Float(), nullable=True)
    )

    op.add_column(
        "network_events",
        sa.Column("message", sa.String(length=255), nullable=True)
    )

    op.add_column(
        "network_events",
        sa.Column("created_at", sa.DateTime(), nullable=True)
    )

    # Copy current values back.
    op.execute(
        """
        UPDATE network_events
        SET network_status = status,
            created_at = recorded_at
        """
    )

    op.drop_column("network_events", "recorded_at")
    op.drop_column("network_events", "status")