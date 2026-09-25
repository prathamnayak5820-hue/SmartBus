from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.bus import Bus
from app.models.trip import Trip
from app.models.parent_student_link import ParentStudentLink
from app.models.gps_location import GPSLocation
from app.models.attendance_record import AttendanceRecord

parent_bp = Blueprint(
    "parent",
    __name__,
    url_prefix="/api/parent"
)


def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


# Parent links a student
@parent_bp.route("/link-student", methods=["POST"])
@jwt_required()
def link_student():

    parent = get_current_user()

    if parent.role != "PARENT":
        return jsonify({
            "message": "Only parents can link students"
        }), 403

    data = request.get_json()

    student_id = data.get("student_id")

    student = Student.query.get(student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    existing = ParentStudentLink.query.filter_by(
        parent_id=parent.id,
        student_id=student.id
    ).first()

    if existing:
        return jsonify({
            "message": "Student already linked"
        }), 409

    link = ParentStudentLink(
        parent_id=parent.id,
        student_id=student.id
    )

    db.session.add(link)
    db.session.commit()

    return jsonify({
        "message": "Student linked successfully",
        "student_id": student.id
    }), 201


# View linked students
@parent_bp.route("/students", methods=["GET"])
@jwt_required()
def get_linked_students():

    parent = get_current_user()

    links = ParentStudentLink.query.filter_by(
        parent_id=parent.id,
        is_active=True
    ).all()

    result = []

    for link in links:
        result.append({
            "student_id": link.student.id,
            "name": link.student.name,
            "usn": link.student.usn,
            "boarding_point": link.student.boarding_point
        })

    return jsonify(result)


# Current bus / presence / GPS / trip information
@parent_bp.route("/student/<int:student_id>/status", methods=["GET"])
@jwt_required()
def student_status(student_id):

    parent = get_current_user()

    link = ParentStudentLink.query.filter_by(
        parent_id=parent.id,
        student_id=student_id,
        is_active=True
    ).first()

    if not link:
        return jsonify({
            "message": "You are not authorized to view this student"
        }), 403

    student = link.student

    attendance = AttendanceRecord.query.filter_by(
        student_id=student.id
    ).order_by(
        AttendanceRecord.updated_at.desc()
    ).first()

    trip = None

    if attendance:
        trip = Trip.query.get(attendance.trip_id)

    gps = None

    if trip:
        gps = GPSLocation.query.filter_by(
            trip_id=trip.id
        ).order_by(
            GPSLocation.recorded_at.desc()
        ).first()

    response = {
        "student": {
            "id": student.id,
            "name": student.name,
            "usn": student.usn,
            "boarding_point": student.boarding_point
        },
        "presence": attendance.status if attendance else "UNKNOWN",
        "trip": None,
        "bus": None,
        "location": None
    }

    if trip:

        bus = Bus.query.get(trip.bus_id)

        response["trip"] = {
            "trip_id": trip.id,
            "status": trip.status,
            "route": trip.route_name
        }

        response["bus"] = {
            "bus_id": bus.id,
            "bus_number": bus.bus_number
        }

    if gps:

        response["location"] = {
            "latitude": gps.latitude,
            "longitude": gps.longitude,
            "speed": gps.speed,
            "recorded_at": gps.recorded_at.isoformat()
        }

    return jsonify(response)