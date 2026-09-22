import uuid
from datetime import datetime

from app.extensions import db


class ParentStudentLink(db.Model):
    __tablename__ = "parent_student_links"

    __table_args__ = (
        db.UniqueConstraint(
            "parent_id",
            "student_id",
            name="uq_parent_student"
        ),
    )

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    parent_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    parent = db.relationship("User")
    student = db.relationship("Student")