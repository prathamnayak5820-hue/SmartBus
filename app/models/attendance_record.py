import uuid
from datetime import datetime

from app.extensions import db


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

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

    status = db.Column(
        db.String(30),
        default="PRESENT",
        nullable=False
    )

    first_seen = db.Column(
        db.DateTime,
        nullable=True
    )

    last_seen = db.Column(
        db.DateTime,
        nullable=True
    )

    left_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )