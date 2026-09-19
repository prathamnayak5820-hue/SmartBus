from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.bus import Bus
from app.models.boarding_point import BoardingPoint


student_bp = Blueprint("students", __name__)


@student_bp.post("/")
@jwt_required()
def create_student():
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can create students"
        }), 403

    data = request.get_json() or {}

    user_id = data.get("user_id")
    student_code = data.get("student_code")
    ble_device_id = data.get("ble_device_id")
    bus_id = data.get("bus_id")
    boarding_point_id = data.get("boarding_point_id")

    if not user_id or not student_code:
        return jsonify({
            "error": "user_id and student_code are required"
        }), 400

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    if user.role != "STUDENT":
        return jsonify({
            "error": "User must have STUDENT role"
        }), 400

    if Student.query.filter_by(student_code=student_code).first():
        return jsonify({
            "error": "Student code already exists"
        }), 409

    if ble_device_id:
        if Student.query.filter_by(
            ble_device_id=ble_device_id
        ).first():
            return jsonify({
                "error": "BLE device already registered"
            }), 409

    if bus_id and not db.session.get(Bus, bus_id):
        return jsonify({
            "error": "Bus not found"
        }), 404

    if boarding_point_id and not db.session.get(
        BoardingPoint, boarding_point_id
    ):
        return jsonify({
            "error": "Boarding point not found"
        }), 404

    student = Student(
        user_id=user_id,
        student_code=student_code,
        ble_device_id=ble_device_id,
        bus_id=bus_id,
        boarding_point_id=boarding_point_id
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student created successfully",
        "student": {
            "id": student.id,
            "student_code": student.student_code,
            "ble_device_id": student.ble_device_id,
            "bus_id": student.bus_id,
            "boarding_point_id": student.boarding_point_id
        }
    }), 201


@student_bp.get("/")
@jwt_required()
def list_students():
    students = Student.query.all()

    result = []

    for student in students:
        user = db.session.get(User, student.user_id)

        result.append({
            "id": student.id,
            "student_code": student.student_code,
            "name": user.name if user else None,
            "phone": user.phone if user else None,
            "bus_id": student.bus_id,
            "boarding_point_id": student.boarding_point_id,
            "ble_registered": bool(student.ble_device_id)
        })

    return jsonify(result), 200


@student_bp.get("/<student_id>")
@jwt_required()
def get_student(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    user = db.session.get(User, student.user_id)

    return jsonify({
        "id": student.id,
        "student_code": student.student_code,
        "name": user.name if user else None,
        "phone": user.phone if user else None,
        "bus_id": student.bus_id,
        "boarding_point_id": student.boarding_point_id,
        "ble_device_id": student.ble_device_id
    }), 200


@student_bp.patch("/<student_id>/assign")
@jwt_required()
def assign_student(student_id):
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can assign students"
        }), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    data = request.get_json() or {}

    if "bus_id" in data:
        bus_id = data.get("bus_id")

        if bus_id and not db.session.get(Bus, bus_id):
            return jsonify({
                "error": "Bus not found"
            }), 404

        student.bus_id = bus_id

    if "boarding_point_id" in data:
        point_id = data.get("boarding_point_id")

        if point_id and not db.session.get(
            BoardingPoint, point_id
        ):
            return jsonify({
                "error": "Boarding point not found"
            }), 404

        student.boarding_point_id = point_id

    db.session.commit()

    return jsonify({
        "message": "Student assignment updated",
        "student_id": student.id,
        "bus_id": student.bus_id,
        "boarding_point_id": student.boarding_point_id
    }), 200