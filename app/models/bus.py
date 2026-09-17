import uuid
from datetime import datetime

from app.extensions import db


class Bus(db.Model):
    __tablename__ = "buses"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    bus_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    driver_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )