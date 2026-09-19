from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db
from app.models.presence_event import PresenceEvent
from app.models.attendance_record import AttendanceRecord
from app.models.student import Student
from app.models.trip import Trip


presence_bp = Blueprint("presence", __name__)

BLE_TIMEOUT_SECONDS = 30


@presence_bp.post("/event")
@jwt_required()
def create_presence_event():

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role != "DRIVER":
        return jsonify({
            "success": False,
            "error": "Only the assigned driver can submit BLE presence events"
        }), 403

    data = request.get_json() or {}

    trip_id = data.get("trip_id")
    student_id = data.get("student_id")
    ble_device_id = data.get("ble_device_id")
    event_type = data.get("event_type", "DETECTED")
    signal_strength = data.get("signal_strength")

    if not trip_id or not student_id or not ble_device_id:
        return jsonify({
            "success": False,
            "error": "trip_id, student_id and ble_device_id are required"
        }), 400

    if event_type not in ["DETECTED", "LEFT"]:
        return jsonify({
            "success": False,
            "error": "event_type must be DETECTED or LEFT"
        }), 400

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({
            "success": False,
            "error": "Trip not found"
        }), 404

    if trip.status != "ACTIVE":
        return jsonify({
            "success": False,
            "error": "BLE presence can only be recorded for an active trip"
        }), 400

    if trip.driver_id != user_id:
        return jsonify({
            "success": False,
            "error": "You are not the assigned driver"
        }), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "success": False,
            "error": "Student not found"
        }), 404

    if student.bus_id != trip.bus_id:
        return jsonify({
            "success": False,
            "error": "Student is not assigned to this bus"
        }), 403

    now = datetime.utcnow()

    detected = event_type == "DETECTED"

    event = PresenceEvent(
        trip_id=trip_id,
        student_id=student.id,
        detected=detected,
        signal_strength=signal_strength,
        ble_device_id=ble_device_id,
        event_type=event_type,
        detected_at=now
    )

    db.session.add(event)

    attendance = AttendanceRecord.query.filter_by(
        trip_id=trip_id,
        student_id=student.id
    ).first()

    if detected:

        if not attendance:

            attendance = AttendanceRecord(
                trip_id=trip_id,
                student_id=student.id,
                status="PRESENT",
                first_seen=now,
                last_seen=now,
                left_at=None
            )

            db.session.add(attendance)

        else:

            attendance.status = "PRESENT"
            attendance.last_seen = now
            attendance.left_at = None

    else:

        if attendance:

            attendance.status = "LEFT"
            attendance.last_seen = now
            attendance.left_at = now

        else:

            attendance = AttendanceRecord(
                trip_id=trip_id,
                student_id=student.id,
                status="LEFT",
                first_seen=None,
                last_seen=now,
                left_at=now
            )

            db.session.add(attendance)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "BLE presence event recorded",
        "event_type": event_type,
        "detected": detected,
        "student_id": student.id,
        "timestamp": now.isoformat()
    }), 201


@presence_bp.post("/<trip_id>/timeout-check")
@jwt_required()
def check_ble_timeout(trip_id):

    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != "DRIVER":
        return jsonify({
            "success": False,
            "error": "Only driver can perform timeout check"
        }), 403

    trip = db.session.get(Trip, trip_id)

    if not trip:
        return jsonify({
            "success": False,
            "error": "Trip not found"
        }), 404

    if trip.driver_id != user_id:
        return jsonify({
            "success": False,
            "error": "You are not assigned to this trip"
        }), 403

    if trip.status != "ACTIVE":
        return jsonify({
            "success": False,
            "error": "Trip is not active"
        }), 400

    cutoff = datetime.utcnow() - timedelta(
        seconds=BLE_TIMEOUT_SECONDS
    )

    present_students = AttendanceRecord.query.filter_by(
        trip_id=trip_id,
        status="PRESENT"
    ).all()

    left_students = []

    for attendance in present_students:

        if attendance.last_seen and attendance.last_seen < cutoff:

            attendance.status = "LEFT"
            attendance.left_at = datetime.utcnow()

            left_students.append(attendance.student_id)

    db.session.commit()

    return jsonify({
        "success": True,
        "timeout_seconds": BLE_TIMEOUT_SECONDS,
        "left_students": left_students,
        "count": len(left_students)
    }), 200


@presence_bp.get("/<trip_id>/attendance")
@jwt_required()
def get_attendance(trip_id):

    records = AttendanceRecord.query.filter_by(
        trip_id=trip_id
    ).all()

    result = []

    for record in records:

        result.append({
            "student_id": record.student_id,
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
        })

    return jsonify({
        "success": True,
        "trip_id": trip_id,
        "attendance": result
    }), 200