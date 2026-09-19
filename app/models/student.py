from app.extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    name = db.Column(db.String(100), nullable=False)

    usn = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    phone = db.Column(db.String(15))

    boarding_point_id = db.Column(
        db.Integer,
        db.ForeignKey("boarding_points.id"),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    boarding_point = db.relationship(
        "BoardingPoint"
    )