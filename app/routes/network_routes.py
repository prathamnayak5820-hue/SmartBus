from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.network_event import NetworkEvent
from app.models.trip import Trip

network_bp = Blueprint("network", __name__)


@network_bp.post("/event")
@jwt_required()
def create_network_event():

    user_id = get_jwt_identity()
    data = request.get_json() or {}

    trip_id = data.get("trip_id")
    source = data.get("source", "DRIVER")
    network_status = data.get("network_status")
    signal_strength = data.get("signal_strength")
    message = data.get("message")

    if not trip_id or not network_status:
        return jsonify({
            "error": "trip_id and network_status are required"
        }), 400

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({
            "error": "Trip not found"
        }), 404

    if trip.driver_id != user_id:
        return jsonify({
            "error": "You are not assigned to this trip"
        }), 403

    event = NetworkEvent(
        trip_id=trip_id,
        source=source,
        network_status=network_status,
        signal_strength=signal_strength,
        message=message
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "Network event recorded successfully",
        "event": {
            "id": event.id,
            "trip_id": event.trip_id,
            "source": event.source,
            "network_status": event.network_status,
            "signal_strength": event.signal_strength,
            "message": event.message,
            "created_at": event.created_at.isoformat()
        }
    }), 201