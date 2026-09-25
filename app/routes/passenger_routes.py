from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.models.trip import Trip
from app.models.student import Student
from app.models.attendance_record import AttendanceRecord


passenger_bp = Blueprint("passenger", __name__)


def get_current_user_id():
    return str(get_jwt_identity())


def get_role():
    return get_jwt().get("role")


@passenger_bp.get("/<trip_id>/passengers")
@jwt_required()
def get_passengers(trip_id):

    current_user_id = get_current_user_id()
    role = get_role()

    trip = Trip.query.get(trip_id)

    if not trip:
        return jsonify({
            "error": "Trip not found"
        }), 404

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if role == "DRIVER":

        if str(trip.driver_id) != current_user_id:
            return jsonify({
                "error": "Access denied"
            }), 403

    elif role in ("ADMIN", "COLLEGE"):
        pass

    elif role in ("STUDENT", "PARENT"):
        pass

    else:
        return jsonify({
            "error": "Access denied"
        }), 403

    # -----------------------------------------------------
    # Get attendance records
    # -----------------------------------------------------

    records = (
        AttendanceRecord.query
        .filter_by(trip_id=trip_id)
        .all()
    )

    present_students = []
    left_students = []
    not_detected_students = []

    for record in records:

        student = Student.query.get(record.student_id)

        if not student:
            continue

        student_data = {
            "student_id": student.id,
            "name": student.name,
            "usn": student.usn,
            "status": record.status,
            "first_seen": (
                record.first_seen.isoformat()
                if record.first_seen else None
            ),
            "last_seen": (
                record.last_seen.isoformat()
                if record.last_seen else None
            ),
            "left_at": (
                record.left_at.isoformat()
                if record.left_at else None
            )
        }

        if record.status == "PRESENT":
            present_students.append(student_data)

        elif record.status == "LEFT":
            left_students.append(student_data)

        elif record.status == "NOT_DETECTED":
            not_detected_students.append(student_data)

    # -----------------------------------------------------
    # Bus capacity
    # -----------------------------------------------------

    bus = trip.bus

    capacity = bus.capacity if bus else None

    passenger_count = len(present_students)

    available_seats = None

    if capacity is not None:
        available_seats = max(
            capacity - passenger_count,
            0
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return jsonify({
        "trip_id": trip.id,
        "bus_id": trip.bus_id,
        "capacity": capacity,
        "passenger_count": passenger_count,
        "available_seats": available_seats,
        "present": present_students,
        "left": left_students,
        "not_detected": not_detected_students
    }), 200