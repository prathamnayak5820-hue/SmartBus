from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.student import Student

student_bp = Blueprint(
    "students",
    __name__,
    url_prefix="/api/students"
)


@student_bp.route("", methods=["POST"])
def create_student():

    data = request.get_json()

    student = Student(
        name=data["name"],
        usn=data["usn"],
        phone=data.get("phone"),
        boarding_point=data.get("boarding_point_id")
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student created",
        "student_id": student.id
    }), 201


@student_bp.route("", methods=["GET"])
def get_students():

    students = Student.query.all()

    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "usn": s.usn,
            "phone": s.phone,
            "boarding_point": s.boarding_point,
            "is_active": s.is_active
        }
        for s in students
    ])