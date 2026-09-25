import uuid
from datetime import datetime

from sqlalchemy import UniqueConstraint

from app.extensions import db


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    __table_args__ = (
        UniqueConstraint(
            "trip_id",
            "student_id",
            name="uq_attendance_trip_student"
        ),
    )

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
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="UNKNOWN",
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
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    trip = db.relationship("Trip")
    student = db.relationship("Student")