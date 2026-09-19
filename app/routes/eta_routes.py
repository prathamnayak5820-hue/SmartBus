from datetime import datetime

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.trip import Trip
from app.models.gps_location import GPSLocation
from app.models.boarding_point import BoardingPoint


eta_bp = Blueprint("eta", __name__)


def haversine_km(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


@eta_bp.get("/<trip_id>")
@jwt_required()
def calculate_eta(trip_id):

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({
            "success": False,
            "error": "Trip not found"
        }), 404

    # Get latest GPS
    latest = (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.desc())
        .first()
    )

    if not latest:
        return jsonify({
            "success": False,
            "error": "No GPS location available for this trip"
        }), 404

    # Get boarding points for this route
    points = (
        BoardingPoint.query
        .filter_by(route_id=trip.route_id)
        .order_by(BoardingPoint.stop_order.asc())
        .all()
    )

    if not points:
        return jsonify({
            "success": False,
            "error": "No boarding points found for this route"
        }), 404

    current_lat = float(latest.latitude)
    current_lon = float(latest.longitude)

    # Find nearest upcoming boarding point
    nearest_point = None
    nearest_distance = None

    for point in points:

        distance = haversine_km(
            current_lat,
            current_lon,
            float(point.latitude),
            float(point.longitude)
        )

        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_point = point

    # Current speed
    current_speed = latest.speed_kmh or 0

    # Minimum safe speed for ETA calculation
    if current_speed < 5:
        current_speed = 20

    # Current GPS-based estimate
    current_eta_minutes = (
        nearest_distance / current_speed
    ) * 60

    # ------------------------------------------------
    # HISTORICAL TRAVEL DATA
    # ------------------------------------------------

    historical_times = []

    completed_trips = (
        Trip.query
        .filter(
            Trip.route_id == trip.route_id,
            Trip.status == "COMPLETED",
            Trip.start_time.isnot(None),
            Trip.end_time.isnot(None)
        )
        .all()
    )

    for old_trip in completed_trips:

        duration_seconds = (
            old_trip.end_time - old_trip.start_time
        ).total_seconds()

        if duration_seconds > 0:
            historical_times.append(
                duration_seconds / 60
            )

    historical_eta = None

    if historical_times:
        historical_eta = (
            sum(historical_times) / len(historical_times)
        )

    # ------------------------------------------------
    # BLEND CURRENT + HISTORICAL INFORMATION
    # ------------------------------------------------

    if historical_eta is not None:

        # More history = more confidence
        if len(historical_times) >= 5:
            historical_weight = 0.6
            current_weight = 0.4

        else:
            historical_weight = 0.3
            current_weight = 0.7

        eta_minutes = (
            current_eta_minutes * current_weight
            + historical_eta * historical_weight
        )

        eta_method = "CURRENT_GPS + HISTORICAL_TRAVEL_TIME"

    else:

        eta_minutes = current_eta_minutes
        eta_method = "CURRENT_GPS_FALLBACK"

    eta_minutes = max(1, round(eta_minutes))

    return jsonify({
        "success": True,

        "trip_id": trip_id,

        "eta": {
            "minutes": eta_minutes,
            "boarding_point": nearest_point.name,
            "distance_km": round(nearest_distance, 2),
            "current_speed_kmh": round(float(current_speed), 2),
            "historical_samples": len(historical_times),
            "historical_average_minutes": (
                round(historical_eta, 2)
                if historical_eta is not None
                else None
            ),
            "method": eta_method,
            "calculated_at": datetime.utcnow().isoformat()
        }
    }), 200