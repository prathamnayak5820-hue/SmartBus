from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.bus import Bus
from app.models.trip import Trip
from app.models.student import Student
from app.models.attendance_record import AttendanceRecord
from app.models.sos_event import SOSEvent

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


def check_admin():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user:
        return None

    if user.role not in ["ADMIN", "COLLEGE"]:
        return None

    return user


@admin_bp.route("/buses", methods=["GET"])
@jwt_required()
def buses():

    if not check_admin():
        return jsonify({
            "message": "Admin access required"
        }), 403

    buses = Bus.query.all()

    return jsonify([
        {
            "id": bus.id,
            "bus_number": bus.bus_number,
            "capacity": bus.capacity,
            "driver_name": bus.driver_name,
            "is_active": bus.is_active
        }
        for bus in buses
    ])


@admin_bp.route("/trips/active", methods=["GET"])
@jwt_required()
def active_trips():

    if not check_admin():
        return jsonify({
            "message": "Admin access required"
        }), 403

    trips = Trip.query.filter_by(
        status="ACTIVE"
    ).all()

    return jsonify([
        {
            "trip_id": trip.id,
            "bus_id": trip.bus_id,
            "route": trip.route_name,
            "status": trip.status
        }
        for trip in trips
    ])


@admin_bp.route("/attendance", methods=["GET"])
@jwt_required()
def attendance():

    if not check_admin():
        return jsonify({
            "message": "Admin access required"
        }), 403

    records = AttendanceRecord.query.all()

    return jsonify([
        {
            "id": record.id,
            "trip_id": record.trip_id,
            "student_id": record.student_id,
            "status": record.status
        }
        for record in records
    ])


@admin_bp.route("/sos", methods=["GET"])
@jwt_required()
def sos():

    if not check_admin():
        return jsonify({
            "message": "Admin access required"
        }), 403

    events = SOSEvent.query.order_by(
        SOSEvent.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": event.id,
            "trip_id": event.trip_id,
            "bus_id": event.bus_id,
            "driver_id": event.driver_id,
            "status": event.status,
            "message": event.message
        }
        for event in events
    ])


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    if not check_admin():
        return jsonify({
            "message": "Admin access required"
        }), 403

    total_buses = Bus.query.count()

    active_buses = Bus.query.filter_by(
        is_active=True
    ).count()

    active_trips = Trip.query.filter_by(
        status="ACTIVE"
    ).count()

    total_students = Student.query.count()

    active_sos = SOSEvent.query.filter_by(
        status="ACTIVE"
    ).count()

    return jsonify({
        "fleet": {
            "total_buses": total_buses,
            "active_buses": active_buses
        },
        "trips": {
            "active": active_trips
        },
        "students": {
            "total": total_students
        },
        "emergency": {
            "active_sos": active_sos
        }
    })