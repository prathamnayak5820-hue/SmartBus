from app.extensions import db


class BoardingPoint(db.Model):
    __tablename__ = "boarding_points"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    stop_order = db.Column(db.Integer)

    is_active = db.Column(db.Boolean, default=True)