from app.extensions import db
from datetime import datetime


class ParentStudentLink(db.Model):
    __tablename__ = "parent_student_links"

    id = db.Column(db.Integer, primary_key=True)

    parent_id = db.Column(
        db.Integer,
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
        default=datetime.utcnow
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    parent = db.relationship("User")
    student = db.relationship("Student")