from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.eta_service import calculate_eta


eta_bp = Blueprint("eta", __name__)


@eta_bp.get("/<trip_id>")
@jwt_required()
def get_eta(trip_id):

    target_boarding_point_id = request.args.get(
        "boarding_point_id"
    )

    result = calculate_eta(
        trip_id=trip_id,
        target_boarding_point_id=target_boarding_point_id
    )

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200