from app.extensions import db
from datetime import datetime


class GPSLocation(db.Model):
    __tablename__ = "gps_locations"

    id = db.Column(db.Integer, primary_key=True)

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey("trips.id"),
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=False
    )

    longitude = db.Column(
        db.Float,
        nullable=False
    )

    speed = db.Column(
        db.Float,
        default=0
    )

    recorded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    trip = db.relationship("Trip")