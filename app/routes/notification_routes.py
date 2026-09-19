from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.notification import Notification
from app.models.user import User

notification_bp = Blueprint(
    "notifications",
    __name__,
    url_prefix="/api/notifications"
)


@notification_bp.route("", methods=["POST"])
@jwt_required()
def create_notification():

    data = request.get_json()

    notification = Notification(
        user_id=data["user_id"],
        notification_type=data["notification_type"],
        title=data["title"],
        message=data["message"],
        trip_id=data.get("trip_id")
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Notification created",
        "notification_id": notification.id
    }), 201


@notification_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():

    user_id = int(get_jwt_identity())

    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": n.id,
            "type": n.notification_type,
            "title": n.title,
            "message": n.message,
            "trip_id": n.trip_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ])


@notification_bp.route("/<int:notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(notification_id):

    user_id = int(get_jwt_identity())

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id
    ).first()

    if not notification:
        return jsonify({
            "message": "Notification not found"
        }), 404

    notification.is_read = True

    db.session.commit()

    return jsonify({
        "message": "Notification marked as read"
    })