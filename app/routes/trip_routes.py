
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import db
from app.models.trip import Trip
from app.models.attendance_record import AttendanceRecord
from app.models.gps_location import GPSLocation
from app.models.notification import Notification
from app.models.sos_event import SOSEvent

trip_bp = Blueprint("trips", __name__)


def trip_data(trip):
    """Convert a Trip model into a JSON-friendly dictionary."""
    return {
        "id": trip.id,
        "bus_id": trip.bus_id,
        "route_id": trip.route_id,
        "driver_id": trip.driver_id,
        "status": trip.status,
        "started_at": (
            trip.started_at.isoformat()
            if trip.started_at else None
        ),
        "ended_at": (
            trip.ended_at.isoformat()
            if trip.ended_at else None
        ),
    }


@trip_bp.post("/")
@jwt_required()
def create_trip():
    data = request.get_json(silent=True) or {}

    bus_id = data.get("bus_id")
    route_id = data.get("route_id")
    driver_id = data.get("driver_id")

    if not bus_id or not route_id or not driver_id:
        return jsonify({
            "error": "bus_id, route_id, and driver_id are required"
        }), 400

    trip = Trip(
        bus_id=bus_id,
        route_id=route_id,
        driver_id=driver_id,
        status="PLANNED"
    )

    db.session.add(trip)
    db.session.commit()

    return jsonify({
        "message": "Trip created successfully",
        "trip_id": trip.id,
        "trip": trip_data(trip)
    }), 201


@trip_bp.delete("/<trip_id>")
@jwt_required()
def delete_trip(trip_id):
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({"error": "Only admin or college can delete trips"}), 403

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    AttendanceRecord.query.filter_by(trip_id=trip_id).delete(
        synchronize_session=False
    )
    GPSLocation.query.filter_by(trip_id=trip_id).delete(
        synchronize_session=False
    )
    Notification.query.filter_by(trip_id=trip_id).delete(
        synchronize_session=False
    )
    SOSEvent.query.filter_by(trip_id=trip_id).delete(
        synchronize_session=False
    )
    db.session.delete(trip)
    db.session.commit()

    return jsonify({
        "message": "Trip deleted successfully",
        "trip_id": trip_id,
    }), 200


@trip_bp.patch("/<trip_id>/start")
@jwt_required()
def start_trip(trip_id):
    user_id = get_jwt_identity()

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    if str(trip.driver_id) != str(user_id):
        return jsonify({
            "error": "You are not assigned to this trip"
        }), 403

    if trip.status != "PLANNED":
        return jsonify({
            "error": "Only planned trips can be started"
        }), 400

    trip.status = "ACTIVE"
    trip.started_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "message": "Trip started successfully",
        "trip_id": trip.id,
        "trip": trip_data(trip),
        "status": trip.status
    }), 200


@trip_bp.patch("/<trip_id>/end")
@jwt_required()
def end_trip(trip_id):
    user_id = get_jwt_identity()

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    if str(trip.driver_id) != str(user_id):
        return jsonify({
            "error": "You are not assigned to this trip"
        }), 403

    if trip.status != "ACTIVE":
        return jsonify({
            "error": "Only active trips can be ended"
        }), 400

    trip.status = "COMPLETED"
    trip.ended_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "message": "Trip completed successfully",
        "trip_id": trip.id,
        "trip": trip_data(trip),
        "status": trip.status
    }), 200