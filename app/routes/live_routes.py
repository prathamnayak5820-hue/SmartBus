from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.models.trip import Trip
from app.models.student import Student
from app.services.live_service import get_live_trip_data


live_bp = Blueprint("live", __name__)


def get_current_user_id():
    return str(get_jwt_identity())


def get_role():
    return get_jwt().get("role")


@live_bp.get("/<trip_id>/live")
@jwt_required()
def get_live_trip(trip_id):
    current_user_id = get_current_user_id()
    role = get_role()

    trip = Trip.query.get(trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    # Admin and college can view any trip
    if role in ("ADMIN", "COLLEGE"):
        pass

    # Assigned driver can view the trip
    elif role == "DRIVER":
        if str(trip.driver_id) != current_user_id:
            return jsonify({"error": "Access denied"}), 403

    # Student can view their own bus trip
    elif role == "STUDENT":
        student = Student.query.filter_by(
            user_id=current_user_id
        ).first()

        if not student:
            return jsonify({"error": "Student profile not found"}), 404

        if str(student.bus_id) != str(trip.bus_id):
            return jsonify({"error": "Access denied"}), 403

    # Parent access will be tightened later using ParentStudentLink
    elif role == "PARENT":
        pass

    else:
        return jsonify({"error": "Access denied"}), 403

    live_data = get_live_trip_data(trip_id)

    return jsonify(live_data), 200