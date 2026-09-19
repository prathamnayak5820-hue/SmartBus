from app.extensions import db
from datetime import datetime


class SOSEvent(db.Model):
    __tablename__ = "sos_events"

    id = db.Column(db.Integer, primary_key=True)

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey("trips.id"),
        nullable=False
    )

    bus_id = db.Column(
        db.Integer,
        db.ForeignKey("buses.id"),
        nullable=False
    )

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(
        db.String(500)
    )

    status = db.Column(
        db.String(30),
        default="ACTIVE"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    resolved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    trip = db.relationship("Trip")
    bus = db.relationship("Bus")
    driver = db.relationship("User")