from app.extensions import db
from app.models.notification import Notification


def create_notification(
    user_id,
    notification_type,
    title,
    message,
    trip_id=None,
    commit=True
):
    """
    Create an in-app notification for a user.

    commit=True:
        Save immediately.

    commit=False:
        Add to the current transaction.
    """

    if not user_id:
        raise ValueError("user_id is required")

    if not notification_type:
        raise ValueError("notification_type is required")

    if not title:
        raise ValueError("title is required")

    if not message:
        raise ValueError("message is required")

    notification = Notification(
        user_id=str(user_id),
        trip_id=trip_id,
        notification_type=notification_type,
        title=title,
        message=message,
        is_read=False
    )

    db.session.add(notification)

    if commit:
        db.session.commit()

    return notification


def get_user_notifications(
    user_id,
    unread_only=False,
    limit=50
):
    """
    Get notifications belonging to a specific user.
    """

    query = Notification.query.filter_by(
        user_id=str(user_id)
    )

    if unread_only:
        query = query.filter_by(
            is_read=False
        )

    return (
        query
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def mark_notification_read(
    notification_id,
    user_id
):
    """
    Mark a user's notification as read.

    A user can only modify their own notification.
    """

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=str(user_id)
    ).first()

    if not notification:
        return None

    notification.is_read = True

    db.session.commit()

    return notification


def mark_all_notifications_read(user_id):
    """
    Mark all notifications belonging to a user as read.
    """

    notifications = Notification.query.filter_by(
        user_id=str(user_id),
        is_read=False
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.session.commit()

    return len(notifications)