from app.extensions import db
from app.models.notification import Notification
from app.models.student import Student
from app.models.user import User
from app.models.parent_student_link import ParentStudentLink
from app.models.trip import Trip


def get_student_user(student):
    """
    Get the User account belonging to a student.
    """

    if not student or not student.user_id:
        return None

    return User.query.get(student.user_id)


def get_parent_users(student_id):
    """
    Get all active parents linked to a student.
    """

    links = ParentStudentLink.query.filter_by(
        student_id=student_id,
        is_active=True
    ).all()

    parent_users = []

    for link in links:
        parent = User.query.get(link.parent_id)

        if parent and parent.is_active:
            parent_users.append(parent)

    return parent_users


def get_notification_users_for_student(student_id):
    """
    Get the student and all active parents linked
    to that student.
    """

    student = Student.query.get(student_id)

    if not student:
        return []

    users = []

    student_user = get_student_user(student)

    if student_user and student_user.is_active:
        users.append(student_user)

    users.extend(
        get_parent_users(student.id)
    )

    return users


def create_user_notification(
    user,
    notification_type,
    title,
    message,
    trip_id=None
):
    """
    Create one notification for one user.
    """

    notification = Notification(
        user_id=user.id,
        trip_id=trip_id,
        notification_type=notification_type,
        title=title,
        message=message,
        is_read=False
    )

    db.session.add(notification)

    return notification


def notify_student_and_parents(
    student_id,
    notification_type,
    title,
    message,
    trip_id=None,
    commit=True
):
    """
    Send an in-app notification to the student
    and all linked parents.
    """

    users = get_notification_users_for_student(
        student_id
    )

    if not users:
        return []

    notifications = []

    # Prevent duplicate notification recipients.
    notified_user_ids = set()

    for user in users:

        if str(user.id) in notified_user_ids:
            continue

        notified_user_ids.add(
            str(user.id)
        )

        notification = create_user_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            trip_id=trip_id
        )

        notifications.append(notification)

    if commit:
        db.session.commit()

    return notifications


def notify_trip_students(
    trip_id,
    notification_type,
    title,
    message,
    commit=True
):
    """
    Notify all students assigned to the bus
    participating in a trip, along with their parents.
    """

    trip = Trip.query.get(trip_id)

    if not trip:
        return []

    students = Student.query.filter_by(
        bus_id=trip.bus_id,
        is_active=True
    ).all()

    notifications = []

    notified_user_ids = set()

    for student in students:

        users = get_notification_users_for_student(
            student.id
        )

        for user in users:

            if str(user.id) in notified_user_ids:
                continue

            notified_user_ids.add(
                str(user.id)
            )

            notification = create_user_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                trip_id=trip.id
            )

            notifications.append(notification)

    if commit:
        db.session.commit()

    return notifications