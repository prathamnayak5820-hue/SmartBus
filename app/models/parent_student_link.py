import uuid
from datetime import datetime

from app.extensions import db


class ParentStudentLink(db.Model):
    __tablename__ = "parent_student_links"

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
        db.String(36),
        db.ForeignKey("students.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )