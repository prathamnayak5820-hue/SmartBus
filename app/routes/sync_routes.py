from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

sync_bp = Blueprint("sync", __name__)


@sync_bp.post("/<trip_id>")
@jwt_required()
def sync_events(trip_id):

    data = request.get_json() or {}

    events = data.get("events", [])

    if not isinstance(events, list):
        return jsonify({
            "success": False,
            "error": "events must be a list"
        }), 400

    processed = 0

    for event in events:

        event_type = event.get("type")

        # Event processing will be connected
        # to GPS / BLE / network services.

        if event_type:
            processed += 1

    return jsonify({
        "success": True,
        "trip_id": trip_id,
        "received": len(events),
        "processed": processed,
        "message": "Offline events accepted for synchronization"
    }), 200