
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.bus import Bus
from app.models.boarding_point import BoardingPoint
from app.models import AttendanceRecord, ParentStudentLink

student_bp = Blueprint("students", __name__)


def student_data(student):
    user = db.session.get(User, student.user_id) if student.user_id else None

    return {
        "id": student.id,
        "name": student.name or (user.name if user else None),
        "usn": student.usn,
        "student_code": student.usn,
        "phone": student.phone or (user.phone if user else None),
        "user_id": student.user_id,
        "bus_id": student.bus_id,
        "boarding_point_id": student.boarding_point_id,
        "ble_device_id": student.ble_device_id,
        "ble_registered": bool(student.ble_device_id),
        "is_active": student.is_active,
    }


@student_bp.post("/")
@jwt_required()
def create_student():
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can create students"
        }), 403

    data = request.get_json() or {}

    name = data.get("name")
    usn = data.get("usn") or data.get("student_code")
    phone = data.get("phone")
    user_id = data.get("user_id")
    ble_device_id = data.get("ble_device_id")
    bus_id = data.get("bus_id")
    boarding_point_id = data.get("boarding_point_id")

    if not name or not usn:
        return jsonify({"error": "name and usn are required"}), 400

    if Student.query.filter_by(usn=usn).first():
        return jsonify({"error": "USN already exists"}), 409

    user = None
    if user_id:
        user = db.session.get(User, user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != "STUDENT":
            return jsonify({"error": "User must have STUDENT role"}), 400

    if ble_device_id and Student.query.filter_by(
        ble_device_id=ble_device_id
    ).first():
        return jsonify({"error": "BLE device already registered"}), 409

    if bus_id and not db.session.get(Bus, bus_id):
        return jsonify({"error": "Bus not found"}), 404

    if boarding_point_id and not db.session.get(
        BoardingPoint, boarding_point_id
    ):
        return jsonify({"error": "Boarding point not found"}), 404

    student = Student(
        user_id=user_id,
        name=name,
        usn=usn,
        phone=phone or (user.phone if user else None),
        ble_device_id=ble_device_id,
        bus_id=bus_id,
        boarding_point_id=boarding_point_id,
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student created successfully",
        "student": student_data(student),
    }), 201


@student_bp.get("/")
@jwt_required()
def list_students():
    students = Student.query.all()

    return jsonify({
        "students": [student_data(student) for student in students]
    }), 200


@student_bp.get("/<int:student_id>")
@jwt_required()
def get_student(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student_data(student)), 200


@student_bp.delete("/<int:student_id>")
@jwt_required()
def delete_student(student_id):
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({"error": "Only admin or college can delete students"}), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    ParentStudentLink.query.filter_by(student_id=student_id).delete(
        synchronize_session=False
    )
    AttendanceRecord.query.filter_by(student_id=student_id).delete(
        synchronize_session=False
    )

    linked_user = db.session.get(User, student.user_id) if student.user_id else None
    db.session.delete(student)
    if linked_user and linked_user.role == "STUDENT":
        db.session.delete(linked_user)
    db.session.commit()

    return jsonify({
        "message": "Student deleted successfully",
        "student_id": student_id,
    }), 200


def update_student_assignment(student_id):
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can assign students"
        }), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json() or {}

    if "bus_id" in data:
        bus_id = data.get("bus_id")

        if bus_id and not db.session.get(Bus, bus_id):
            return jsonify({"error": "Bus not found"}), 404

        student.bus_id = bus_id

    if "boarding_point_id" in data:
        point_id = data.get("boarding_point_id")

        if point_id and not db.session.get(BoardingPoint, point_id):
            return jsonify({"error": "Boarding point not found"}), 404

        student.boarding_point_id = point_id

    db.session.commit()

    return jsonify({
        "message": "Student assignment updated",
        "student_id": student.id,
        "bus_id": student.bus_id,
        "boarding_point_id": student.boarding_point_id,
    }), 200


@student_bp.patch("/<int:student_id>/assign")
@jwt_required()
def assign_student(student_id):
    return update_student_assignment(student_id)


@student_bp.patch("/<int:student_id>/bus")
@jwt_required()
def assign_student_bus(student_id):
    return update_student_assignment(student_id)


@student_bp.get("/<int:student_id>/attendance")
@jwt_required()
def get_student_attendance(student_id):
    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    records = AttendanceRecord.query.filter_by(
        student_id=student_id
    ).all()

    attendance = [
        {
            "id": record.id,
            "trip_id": record.trip_id,
            "student_id": record.student_id,
            "status": record.status,
        }
        for record in records
    ]

    return jsonify({
        "student_id": student_id,
        "attendance": attendance,
    }), 200