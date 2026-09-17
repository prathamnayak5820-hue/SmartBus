import uuid
from datetime import datetime

from app.extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    student_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    ble_device_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    bus_id = db.Column(
        db.String(36),
        db.ForeignKey("buses.id"),
        nullable=True
    )

    boarding_point_id = db.Column(
        db.String(36),
        db.ForeignKey("boarding_points.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )