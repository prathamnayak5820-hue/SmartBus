from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.route import Route
from app.models.boarding_point import BoardingPoint


route_bp = Blueprint("routes", __name__)


@route_bp.post("/")
@jwt_required()
def create_route():
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can create routes"
        }), 403

    data = request.get_json() or {}

    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({
            "error": "Route name is required"
        }), 400

    route = Route(
        name=name,
        description=description
    )

    db.session.add(route)
    db.session.commit()

    return jsonify({
        "message": "Route created successfully",
        "route": {
            "id": route.id,
            "name": route.name,
            "description": route.description
        }
    }), 201


@route_bp.get("/")
@jwt_required()
def list_routes():
    routes = Route.query.all()

    result = []

    for route in routes:
        result.append({
            "id": route.id,
            "name": route.name,
            "description": route.description
        })

    return jsonify(result), 200


@route_bp.get("/<route_id>")
@jwt_required()
def get_route(route_id):
    route = db.session.get(Route, route_id)

    if not route:
        return jsonify({
            "error": "Route not found"
        }), 404

    points = BoardingPoint.query.filter_by(
        route_id=route.id
    ).order_by(
        BoardingPoint.stop_order
    ).all()

    return jsonify({
        "id": route.id,
        "name": route.name,
        "description": route.description,
        "boarding_points": [
            {
                "id": point.id,
                "name": point.name,
                "latitude": float(point.latitude),
                "longitude": float(point.longitude),
                "stop_order": point.stop_order,
                "geofence_radius_m": point.geofence_radius_m
            }
            for point in points
        ]
    }), 200


@route_bp.post("/<route_id>/boarding-points")
@jwt_required()
def add_boarding_point(route_id):
    claims = get_jwt()

    if claims.get("role") not in ["ADMIN", "COLLEGE"]:
        return jsonify({
            "error": "Only admin or college can add boarding points"
        }), 403

    route = db.session.get(Route, route_id)

    if not route:
        return jsonify({
            "error": "Route not found"
        }), 404

    data = request.get_json() or {}

    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    stop_order = data.get("stop_order")
    geofence_radius_m = data.get("geofence_radius_m", 200)

    if (
        not name
        or latitude is None
        or longitude is None
        or stop_order is None
    ):
        return jsonify({
            "error": "name, latitude, longitude and stop_order are required"
        }), 400

    point = BoardingPoint(
        route_id=route.id,
        name=name,
        latitude=latitude,
        longitude=longitude,
        stop_order=stop_order,
        geofence_radius_m=geofence_radius_m
    )

    db.session.add(point)
    db.session.commit()

    return jsonify({
        "message": "Boarding point added successfully",
        "boarding_point": {
            "id": point.id,
            "route_id": point.route_id,
            "name": point.name,
            "latitude": float(point.latitude),
            "longitude": float(point.longitude),
            "stop_order": point.stop_order,
            "geofence_radius_m": point.geofence_radius_m
        }
    }), 201