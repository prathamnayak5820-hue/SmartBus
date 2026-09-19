from app.extensions import db
from datetime import datetime


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.String(36), primary_key=True)

    bus_id = db.Column(
        db.Integer,
        db.ForeignKey("buses.id"),
        nullable=False
    )

    
    route_id = db.Column(
    db.String(36),
    db.ForeignKey("routes.id"),
    nullable=False
)

    status = db.Column(
        db.String(30),
        default="SCHEDULED"
    )

    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)

    bus = db.relationship("Bus")
    route = db.relationship("Route")