"""add bus and BLE fields to students

Revision ID: add_student_bus_ble
Revises: reconcile_network_events
"""

from alembic import op
import sqlalchemy as sa


revision = "add_student_bus_ble"
down_revision = "reconcile_network_events"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "students",
        sa.Column(
            "bus_id",
            sa.String(length=36),
            nullable=True
        )
    )

    op.add_column(
        "students",
        sa.Column(
            "ble_device_id",
            sa.String(length=100),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_students_bus_id",
        "students",
        "buses",
        ["bus_id"],
        ["id"]
    )

    op.create_unique_constraint(
        "uq_students_ble_device_id",
        "students",
        ["ble_device_id"]
    )


def downgrade():

    op.drop_constraint(
        "uq_students_ble_device_id",
        "students",
        type_="unique"
    )

    op.drop_constraint(
        "fk_students_bus_id",
        "students",
        type_="foreignkey"
    )

    op.drop_column(
        "students",
        "ble_device_id"
    )

    op.drop_column(
        "students",
        "bus_id"
    )