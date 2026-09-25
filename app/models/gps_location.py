import uuid
from datetime import datetime

from app.extensions import db


class GPSLocation(db.Model):
    __tablename__ = "gps_locations"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Unique ID of the original GPS event.
    # Used for idempotent offline synchronization.
    event_id = db.Column(
        db.String(36),
        unique=True,
        nullable=True
    )

    trip_id = db.Column(
        db.String(36),
        db.ForeignKey("trips.id"),
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=False
    )

    longitude = db.Column(
        db.Float,
        nullable=False
    )

    speed_kmh = db.Column(
        db.Float,
        nullable=True
    )

    accuracy_m = db.Column(
        db.Float,
        nullable=True
    )

    source = db.Column(
        db.String(40),
        default="DRIVER",
        nullable=False
    )

    network_status = db.Column(
        db.String(30),
        default="ONLINE",
        nullable=False
    )

    recorded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    trip = db.relationship("Trip")