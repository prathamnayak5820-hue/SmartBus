from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.bus import Bus
from app.models.user import User


bus_bp = Blueprint("bus", __name__)


@bus_bp.get("/health")
def bus_health():
    return {
        "message": "Bus routes are working",
        "status": "success"
    }


@bus_bp.post("/")
@jwt_required()
def create_bus():
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can create buses"
        }), 403

    data = request.get_json() or {}

    bus_number = data.get("bus_number")
    capacity = data.get("capacity")
    driver_id = data.get("driver_id")

    if not bus_number or capacity is None:
        return jsonify({
            "error": "bus_number and capacity are required"
        }), 400

    if Bus.query.filter_by(bus_number=bus_number).first():
        return jsonify({
            "error": "Bus number already exists"
        }), 409

    if driver_id:
        driver = db.session.get(User, driver_id)

        if not driver:
            return jsonify({
                "error": "Driver not found"
            }), 404

        if driver.role != "DRIVER":
            return jsonify({
                "error": "Selected user is not a driver"
            }), 400

    bus = Bus(
        bus_number=bus_number,
        capacity=capacity,
        driver_id=driver_id
    )

    db.session.add(bus)
    db.session.commit()

    return jsonify({
        "message": "Bus created successfully",
        "bus": {
            "id": bus.id,
            "bus_number": bus.bus_number,
            "capacity": bus.capacity,
            "driver_id": bus.driver_id,
            "is_active": bus.is_active
        }
    }), 201


@bus_bp.get("/")
@jwt_required()
def list_buses():
    buses = Bus.query.all()

    result = []

    for bus in buses:
        result.append({
            "id": bus.id,
            "bus_number": bus.bus_number,
            "capacity": bus.capacity,
            "driver_id": bus.driver_id,
            "is_active": bus.is_active
        })

    return jsonify(result), 200


@bus_bp.get("/<bus_id>")
@jwt_required()
def get_bus(bus_id):
    bus = db.session.get(Bus, bus_id)

    if not bus:
        return jsonify({
            "error": "Bus not found"
        }), 404

    return jsonify({
        "id": bus.id,
        "bus_number": bus.bus_number,
        "capacity": bus.capacity,
        "driver_id": bus.driver_id,
        "is_active": bus.is_active
    }), 200


@bus_bp.patch("/<bus_id>/assign-driver")
@jwt_required()
def assign_driver(bus_id):
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can assign drivers"
        }), 403

    bus = db.session.get(Bus, bus_id)

    if not bus:
        return jsonify({
            "error": "Bus not found"
        }), 404

    data = request.get_json() or {}
    driver_id = data.get("driver_id")

    if not driver_id:
        return jsonify({
            "error": "driver_id is required"
        }), 400

    driver = db.session.get(User, driver_id)

    if not driver:
        return jsonify({
            "error": "Driver not found"
        }), 404

    if driver.role != "DRIVER":
        return jsonify({
            "error": "User is not a driver"
        }), 400

    bus.driver_id = driver_id
    db.session.commit()

    return jsonify({
        "message": "Driver assigned successfully",
        "bus_id": bus.id,
        "driver_id": bus.driver_id
    }), 200