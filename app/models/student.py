from app.extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    # UUID-based User ID
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=True
    )

    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15))

    # Optional BLE device identifier
    ble_device_id = db.Column(db.String(100), nullable=True)

    # UUID-based Bus ID
    bus_id = db.Column(
        db.String(36),
        db.ForeignKey("buses.id"),
        nullable=True
    )

    boarding_point_id = db.Column(
        db.Integer,
        db.ForeignKey("boarding_points.id"),
        nullable=True
    )

    is_active = db.Column(db.Boolean, default=True)

    boarding_point = db.relationship("BoardingPoint")
    bus = db.relationship("Bus")
    user = db.relationship("User")