import uuid
from datetime import datetime

from app.extensions import db


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    bus_id = db.Column(
        db.String(36),
        db.ForeignKey("buses.id"),
        nullable=False
    )

    route_id = db.Column(
        db.String(36),
        db.ForeignKey("routes.id"),
        nullable=False
    )

    driver_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="PLANNED",
        nullable=False
    )

    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )