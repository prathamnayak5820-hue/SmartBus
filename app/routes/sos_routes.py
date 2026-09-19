from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.models.trip import Trip
from app.models.sos_event import SOSEvent

sos_bp = Blueprint(
    "sos",
    __name__,
    url_prefix="/api/sos"
)

@sos_bp.route("", methods=["POST"])
@jwt_required()
def create_sos():

    driver_id = get_jwt_identity()

    driver = User.query.get(driver_id)

    if not driver:
        return jsonify({
            "message": "Driver not found"
        }), 404

    if driver.role != "DRIVER":
        return jsonify({
            "message": "Only drivers can trigger SOS"
        }), 403

    data = request.get_json()

    trip = Trip.query.get(data.get("trip_id"))

    if not trip:
        return jsonify({
            "message": "Trip not found"
        }), 404

    if trip.status != "ACTIVE":
        return jsonify({
            "message": "SOS can only be created for an active trip"
        }), 400

    sos = SOSEvent(
        trip_id=trip.id,
        bus_id=trip.bus_id,
        driver_id=driver.id,
        message=data.get(
            "message",
            "Emergency SOS triggered"
        )
    )

    db.session.add(sos)
    db.session.commit()

    return jsonify({
        "message": "SOS created successfully",
        "sos_id": sos.id,
        "trip_id": trip.id,
        "bus_id": trip.bus_id,
        "status": sos.status
    }), 201




@sos_bp.route("", methods=["GET"])
@jwt_required()
def get_sos_events():

    events = SOSEvent.query.order_by(
        SOSEvent.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": event.id,
            "trip_id": event.trip_id,
            "bus_id": event.bus_id,
            "driver_id": event.driver_id,
            "message": event.message,
            "status": event.status,
            "created_at": event.created_at.isoformat()
        }
        for event in events
    ])


@sos_bp.route("/<int:sos_id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_sos(sos_id):

    sos = SOSEvent.query.get(sos_id)

    if not sos:
        return jsonify({
            "message": "SOS not found"
        }), 404

    sos.status = "RESOLVED"
    sos.resolved_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "SOS resolved",
        "sos_id": sos.id,
        "status": sos.status
    })