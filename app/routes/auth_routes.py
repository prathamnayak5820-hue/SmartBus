from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")
    password = data.get("password")
    role = data.get("role", "STUDENT")

    if not name or not phone or not password:
        return jsonify({
            "error": "name, phone and password are required"
        }), 400

    existing_user = User.query.filter_by(phone=phone).first()

    if existing_user:
        return jsonify({
            "error": "Phone number already registered"
        }), 409

    password_hash = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    user = User(
        name=name,
        phone=phone,
        password_hash=password_hash,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()

    phone = data.get("phone")
    password = data.get("password")

    user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({
            "error": "Invalid phone or password"
        }), 401

    valid_password = bcrypt.check_password_hash(
        user.password_hash,
        password
    )

    if not valid_password:
        return jsonify({
            "error": "Invalid phone or password"
        }), 401

    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "role": user.role
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "role": user.role
        }
    }), 200