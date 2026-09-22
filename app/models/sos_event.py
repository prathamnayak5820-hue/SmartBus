import uuid
from datetime import datetime

from app.extensions import db


class SOSEvent(db.Model):
    __tablename__ = "sos_events"

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

    bus_id = db.Column(
        db.String(36),
        db.ForeignKey("buses.id"),
        nullable=False
    )

    driver_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    message = db.Column(db.Text)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    resolved_at = db.Column(db.DateTime, nullable=True)