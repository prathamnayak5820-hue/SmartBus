from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db
from app.models.gps_location import GPSLocation
from app.models.trip import Trip
from app.models.student import Student

gps_bp = Blueprint("gps", __name__)


@gps_bp.post("/")
@jwt_required()
def add_gps_location():

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    data = request.get_json() or {}

    trip_id = data.get("trip_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    speed_kmh = data.get("speed_kmh")
    accuracy_m = data.get("accuracy_m")
    network_status = data.get("network_status", "ONLINE")

    if not trip_id or latitude is None or longitude is None:
        return jsonify({
            "error": "trip_id, latitude and longitude are required"
        }), 400

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    if trip.status != "ACTIVE":
        return jsonify({
            "error": "GPS can only be sent for an active trip"
        }), 400

    # DRIVER GPS
    if role == "DRIVER":

        if trip.driver_id != user_id:
            return jsonify({
                "error": "You are not assigned to this trip"
            }), 403

        source = "DRIVER"

    # STUDENT FALLBACK GPS
    elif role == "STUDENT":

        student = Student.query.filter_by(user_id=user_id).first()

        if not student:
            return jsonify({
                "error": "Student profile not found"
            }), 404

        bus = db.session.get(
            __import__("app.models.bus", fromlist=["Bus"]).Bus,
            trip.bus_id
        )

        if not bus:
            return jsonify({
                "error": "Bus not found"
            }), 404

        if student.bus_id != trip.bus_id:
            return jsonify({
                "error": "Student is not assigned to this bus"
            }), 403

        source = "STUDENT"

    else:
        return jsonify({
            "error": "Only driver or assigned student can submit GPS"
        }), 403

    location = GPSLocation(
        trip_id=trip_id,
        latitude=latitude,
        longitude=longitude,
        speed_kmh=speed_kmh,
        accuracy_m=accuracy_m,
        source=source,
        network_status=network_status
    )

    db.session.add(location)
    db.session.commit()

    return jsonify({
        "message": "GPS location recorded successfully",
        "location": {
            "id": location.id,
            "trip_id": location.trip_id,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "speed_kmh": location.speed_kmh,
            "accuracy_m": location.accuracy_m,
            "source": location.source,
            "network_status": location.network_status,
            "recorded_at": location.recorded_at.isoformat()
        }
    }), 201


@gps_bp.get("/<trip_id>/latest")
@jwt_required()
def latest_gps_location(trip_id):

    location = (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.desc())
        .first()
    )

    if not location:
        return jsonify({
            "error": "No GPS location found for this trip"
        }), 404

    return jsonify({
        "trip_id": trip_id,
        "latitude": float(location.latitude),
        "longitude": float(location.longitude),
        "speed_kmh": location.speed_kmh,
        "accuracy_m": location.accuracy_m,
        "source": location.source,
        "network_status": location.network_status,
        "recorded_at": location.recorded_at.isoformat()
    }), 200