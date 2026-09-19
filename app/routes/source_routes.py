from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.gps_location import GPSLocation


source_bp = Blueprint("source", __name__)


@source_bp.get("/<trip_id>")
@jwt_required()
def get_source_status(trip_id):

    locations = (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.desc())
        .limit(20)
        .all()
    )

    driver = None
    student = None

    for location in locations:

        if location.source == "DRIVER" and driver is None:
            driver = location

        if location.source == "STUDENT" and student is None:
            student = location

    if driver:
        selected = driver
        selected_source = "DRIVER"
        mode = "PRIMARY"

    elif student:
        selected = student
        selected_source = "STUDENT"
        mode = "FALLBACK"

    else:
        selected = None
        selected_source = None
        mode = "LAST_KNOWN_OR_OFFLINE"

    return jsonify({
        "success": True,
        "trip_id": trip_id,
        "selected_source": selected_source,
        "mode": mode,
        "location": {
            "latitude": float(selected.latitude),
            "longitude": float(selected.longitude),
            "recorded_at": selected.recorded_at.isoformat()
        } if selected else None
    }), 200