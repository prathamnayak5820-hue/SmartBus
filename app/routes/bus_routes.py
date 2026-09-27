
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.bus import Bus
from app.models.user import User


bus_bp = Blueprint("bus", __name__)


def bus_data(bus):
    return {
        "id": bus.id,
        "bus_number": bus.bus_number,
        "capacity": bus.capacity,
        "driver_id": bus.driver_id,
        "is_active": bus.is_active,
    }


def is_admin():
    return get_jwt().get("role") in ["ADMIN", "COLLEGE"]


def error_response(message, status):
    return jsonify({"error": message}), status


@bus_bp.get("/health")
def bus_health():
    return {
        "message": "Bus routes are working",
        "status": "success",
    }


@bus_bp.post("/")
@jwt_required()
def create_bus():
    if not is_admin():
        return error_response(
            "Only admin or college can create buses", 403
        )

    data = request.get_json(silent=True) or {}

    bus_number = data.get("bus_number")
    capacity = data.get("capacity")
    driver_id = data.get("driver_id")

    if not bus_number or capacity is None:
        return error_response(
            "bus_number and capacity are required", 400
        )

    try:
        capacity = int(capacity)
    except (TypeError, ValueError):
        return error_response("capacity must be an integer", 400)

    if capacity <= 0:
        return error_response("capacity must be positive", 400)

    if Bus.query.filter_by(bus_number=bus_number).first():
        return error_response("Bus number already exists", 409)

    if driver_id:
        driver = db.session.get(User, driver_id)

        if not driver:
            return error_response("Driver not found", 404)

        if driver.role != "DRIVER":
            return error_response(
                "Selected user is not a driver", 400
            )

    bus = Bus(
        bus_number=bus_number,
        capacity=capacity,
        driver_id=driver_id,
    )

    db.session.add(bus)
    db.session.commit()

    return jsonify({
        "message": "Bus created successfully",
        "bus": bus_data(bus),
    }), 201


@bus_bp.get("/")
@jwt_required()
def list_buses():
    role = get_jwt().get("role")

    query = Bus.query

    # Drivers can only see buses assigned to them.
    if role == "DRIVER":
        from flask_jwt_extended import get_jwt_identity
        query = query.filter_by(
            driver_id=get_jwt_identity()
        )

    buses = query.all()

    return jsonify([bus_data(bus) for bus in buses]), 200


@bus_bp.get("/<bus_id>")
@jwt_required()
def get_bus(bus_id):
    bus = db.session.get(Bus, bus_id)

    if not bus:
        return error_response("Bus not found", 404)

    role = get_jwt().get("role")

    if role == "DRIVER":
        from flask_jwt_extended import get_jwt_identity

        if str(bus.driver_id) != str(get_jwt_identity()):
            return error_response(
                "You are not assigned to this bus", 403
            )

    return jsonify(bus_data(bus)), 200


@bus_bp.patch("/<bus_id>/assign-driver")
@jwt_required()
def assign_driver(bus_id):
    if not is_admin():
        return error_response(
            "Only admin or college can assign drivers", 403
        )

    bus = db.session.get(Bus, bus_id)

    if not bus:
        return error_response("Bus not found", 404)

    data = request.get_json(silent=True) or {}
    driver_id = data.get("driver_id")

    if not driver_id:
        return error_response("driver_id is required", 400)

    driver = db.session.get(User, driver_id)

    if not driver:
        return error_response("Driver not found", 404)

    if driver.role != "DRIVER":
        return error_response("User is not a driver", 400)

    bus.driver_id = driver_id
    db.session.commit()

    return jsonify({
        "message": "Driver assigned successfully",
        "bus_id": bus.id,
        "driver_id": bus.driver_id,
    }), 200