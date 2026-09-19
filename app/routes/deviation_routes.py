from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

deviation_bp = Blueprint("deviation", __name__)


@deviation_bp.post("/check")
@jwt_required()
def check_deviation():

    data = request.get_json() or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    route_latitude = data.get("route_latitude")
    route_longitude = data.get("route_longitude")
    allowed_radius_m = data.get("allowed_radius_m", 300)

    if None in [
        latitude,
        longitude,
        route_latitude,
        route_longitude
    ]:
        return jsonify({
            "success": False,
            "error": "GPS and route reference coordinates required"
        }), 400

    from math import radians, sin, cos, sqrt, atan2

    R = 6371000

    dlat = radians(
        latitude - route_latitude
    )

    dlon = radians(
        longitude - route_longitude
    )

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(route_latitude))
        * cos(radians(latitude))
        * sin(dlon / 2) ** 2
    )

    distance = R * 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    deviation = distance > allowed_radius_m

    return jsonify({
        "success": True,
        "distance_from_route_m": round(distance, 2),
        "allowed_radius_m": allowed_radius_m,
        "route_deviation": deviation
    }), 200