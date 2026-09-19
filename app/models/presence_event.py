import uuid
from datetime import datetime

from app.extensions import db


class PresenceEvent(db.Model):
    __tablename__ = "presence_events"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    trip_id = db.Column(
        db.String(36),
        db.ForeignKey("trips.id"),
        nullable=False
    )

    student_id = db.Column(
        db.String(36),
        db.ForeignKey("students.id"),
        nullable=False
    )

    detected = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    signal_strength = db.Column(
        db.Integer,
        nullable=True
    )

    ble_device_id = db.Column(
        db.String(100),
        nullable=True
    )

    event_type = db.Column(
        db.String(30),
        nullable=True
    )

    detected_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )