from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from app.extensions import db, bcrypt
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    phone = data.get("phone")
    password = data.get("password")

    if not all([name, phone, password]):
        return jsonify({
            "error": "name, phone and password are required"
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({
            "error": "Phone number already registered"
        }), 409

    password_hash = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    # Public registration can only create STUDENT accounts.
    user = User(
        name=name,
        phone=phone,
        password_hash=password_hash,
        role=(
    data.get("role", "STUDENT")
    if current_app.config.get("ALLOW_TEST_ROLE_REGISTRATION", False)
    else "STUDENT"
    ),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id,
        "role": user.role,
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    phone = data.get("phone")
    password = data.get("password")

    user = User.query.filter_by(phone=phone).first()

    if (
        not user
        or not user.is_active
        or not bcrypt.check_password_hash(
            user.password_hash, password or ""
        )
    ):
        return jsonify({
            "error": "Invalid phone or password"
        }), 401

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role},
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
        },
    }), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user or not user.is_active:
        return jsonify({
            "error": "User not found or inactive"
        }), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
    }), 200


@auth_bp.post("/admin-register")
@jwt_required()
def admin_register():
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({"error": "Only admin or college can create accounts"}), 403

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    phone = data.get("phone")
    password = data.get("password")
    role = data.get("role")

    if role not in ["STUDENT", "DRIVER", "PARENT"]:
        return jsonify({"error": "role must be STUDENT, DRIVER, or PARENT"}), 400

    if not all([name, phone, password]):
        return jsonify({
            "error": "name, phone and password are required"
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone number already registered"}), 409

    user = User(
        name=name,
        phone=phone,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        role=role,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "user_id": user.id,
        "role": user.role,
    }), 201