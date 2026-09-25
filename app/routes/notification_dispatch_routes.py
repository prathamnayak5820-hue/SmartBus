from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.services.notification_dispatch_service import (
    notify_student_and_parents,
    notify_trip_students,
)


notification_dispatch_bp = Blueprint(
    "notification_dispatch",
    __name__
)


def is_admin_or_college():
    role = get_jwt().get("role")
    return role in ("ADMIN", "COLLEGE")


@notification_dispatch_bp.post("/dispatch")
@jwt_required()
def dispatch_notification():

    if not is_admin_or_college():
        return jsonify({
            "error": "Access denied"
        }), 403

    data = request.get_json(silent=True) or {}

    notification_type = data.get("notification_type")
    title = data.get("title")
    message = data.get("message")

    student_id = data.get("student_id")
    trip_id = data.get("trip_id")

    if not notification_type:
        return jsonify({
            "error": "notification_type is required"
        }), 400

    if not title:
        return jsonify({
            "error": "title is required"
        }), 400

    if not message:
        return jsonify({
            "error": "message is required"
        }), 400

    if not student_id and not trip_id:
        return jsonify({
            "error": "student_id or trip_id is required"
        }), 400

    if student_id and trip_id:
        return jsonify({
            "error": "Provide either student_id or trip_id, not both"
        }), 400

    try:

        if student_id:

            notifications = notify_student_and_parents(
                student_id=student_id,
                notification_type=notification_type,
                title=title,
                message=message,
                trip_id=trip_id
            )

        else:

            notifications = notify_trip_students(
                trip_id=trip_id,
                notification_type=notification_type,
                title=title,
                message=message
            )

        if not notifications:
            return jsonify({
                "message": "No notification recipients found",
                "created_count": 0
            }), 200

        return jsonify({
            "message": "Notifications dispatched",
            "created_count": len(notifications),
            "notification_ids": [
                notification.id
                for notification in notifications
            ]
        }), 201

    except Exception:
        return jsonify({
            "error": "Failed to dispatch notification"
        }), 500