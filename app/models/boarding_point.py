import uuid

from app.extensions import db


class BoardingPoint(db.Model):
    __tablename__ = "boarding_points"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    route_id = db.Column(
        db.String(36),
        db.ForeignKey("routes.id"),
        nullable=False
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    latitude = db.Column(
        db.Numeric(9, 6),
        nullable=False
    )

    longitude = db.Column(
        db.Numeric(9, 6),
        nullable=False
    )

    stop_order = db.Column(
        db.Integer,
        nullable=False
    )

    geofence_radius_m = db.Column(
        db.Integer,
        default=200
    )