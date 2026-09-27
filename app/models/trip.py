
import uuid

from app.extensions import db


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    bus_id = db.Column(
        db.String(36),
        db.ForeignKey("buses.id"),
        nullable=False
    )

    route_id = db.Column(
        db.String(36),
        db.ForeignKey("routes.id"),
        nullable=False
    )

    driver_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="SCHEDULED"
    )

    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)

    bus = db.relationship("Bus")
    route = db.relationship("Route")
    driver = db.relationship("User")