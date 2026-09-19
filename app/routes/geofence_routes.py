from math import radians, sin, cos, sqrt, atan2

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.boarding_point import BoardingPoint


geofence_bp = Blueprint("geofence", __name__)


def distance_km(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return R * 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )


@geofence_bp.post("/evaluate")
@jwt_required()
def evaluate_geofence():

    data = request.get_json() or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    boarding_point_id = data.get("boarding_point_id")

    if latitude is None or longitude is None or not boarding_point_id:
        return jsonify({
            "success": False,
            "error": "latitude, longitude and boarding_point_id required"
        }), 400

    point = db.session.get(
        BoardingPoint,
        boarding_point_id
    )

    if not point:
        return jsonify({
            "success": False,
            "error": "Boarding point not found"
        }), 404

    distance = distance_km(
        float(latitude),
        float(longitude),
        float(point.latitude),
        float(point.longitude)
    )

    distance_m = distance * 1000

    radius = point.geofence_radius_m or 200

    inside = distance_m <= radius

    return jsonify({
        "success": True,
        "boarding_point": point.name,
        "distance_m": round(distance_m, 2),
        "geofence_radius_m": radius,
        "inside_geofence": inside,
        "notification_required": inside
    }), 200