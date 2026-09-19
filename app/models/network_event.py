import uuid
from datetime import datetime

from app.extensions import db


class NetworkEvent(db.Model):
    __tablename__ = "network_events"

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

    source = db.Column(
        db.String(40),
        nullable=False
    )

    network_status = db.Column(
        db.String(30),
        nullable=False
    )

    signal_strength = db.Column(
        db.Float,
        nullable=True
    )

    message = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )