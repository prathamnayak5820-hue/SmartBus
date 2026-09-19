from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.bus import Bus

bus_bp = Blueprint(
    "buses",
    __name__,
    url_prefix="/api/buses"
)


@bus_bp.route("", methods=["POST"])
def create_bus():
    data = request.get_json()

    bus = Bus(
        bus_number=data["bus_number"],
        capacity=data["capacity"]
    )

    db.session.add(bus)
    db.session.commit()

    return jsonify({
        "message": "Bus created successfully",
        "bus_id": bus.id
    }), 201


@bus_bp.route("", methods=["GET"])
def get_buses():
    buses = Bus.query.all()

    return jsonify([
        {
            "id": bus.id,
            "bus_number": bus.bus_number,
            "capacity": bus.capacity,
            "is_active": bus.is_active
        }
        for bus in buses
    ])