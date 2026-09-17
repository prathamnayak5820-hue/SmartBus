from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.trip import Trip

trip_bp = Blueprint("trips", __name__)


@trip_bp.post("/")
@jwt_required()
def create_trip():
    data = request.get_json()

    trip = Trip(
        bus_id=data.get("bus_id"),
        route_id=data.get("route_id"),
        driver_id=data.get("driver_id"),
        status="PLANNED"
    )

    db.session.add(trip)
    db.session.commit()

    return jsonify({
        "message": "Trip created successfully",
        "trip_id": trip.id
    }), 201


@trip_bp.patch("/<trip_id>/start")
@jwt_required()
def start_trip(trip_id):
    user_id = get_jwt_identity()

    trip = Trip.query.get(trip_id)

    if not trip:
        return jsonify({
            "error": "Trip not found"
        }), 404

    if trip.driver_id != user_id:
        return jsonify({
            "error": "You are not assigned to this trip"
        }), 403

    if trip.status != "PLANNED":
        return jsonify({
            "error": "Only planned trips can be started"
        }), 400

    trip.status = "ACTIVE"
    trip.start_time = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Trip started successfully",
        "trip_id": trip.id,
        "status": trip.status
    }), 200


@trip_bp.patch("/<trip_id>/end")
@jwt_required()
def end_trip(trip_id):
    user_id = get_jwt_identity()

    trip = Trip.query.get(trip_id)

    if not trip:
        return jsonify({
            "error": "Trip not found"
        }), 404

    if trip.driver_id != user_id:
        return jsonify({
            "error": "You are not assigned to this trip"
        }), 403

    if trip.status != "ACTIVE":
        return jsonify({
            "error": "Only active trips can be ended"
        }), 400

    trip.status = "COMPLETED"
    trip.end_time = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Trip completed successfully",
        "trip_id": trip.id,
        "status": trip.status
    }), 200