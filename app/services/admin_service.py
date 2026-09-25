from app.models.user import User
from app.models.student import Student
from app.models.bus import Bus
from app.models.trip import Trip
from app.models.attendance_record import AttendanceRecord
from app.models.sos_event import SOSEvent


def get_admin_dashboard():

    total_students = Student.query.filter_by(
        is_active=True
    ).count()

    total_buses = Bus.query.filter_by(
        is_active=True
    ).count()

    total_drivers = User.query.filter_by(
        role="DRIVER",
        is_active=True
    ).count()

    active_trips = Trip.query.filter_by(
        status="ACTIVE"
    ).count()

    planned_trips = Trip.query.filter_by(
        status="PLANNED"
    ).count()

    completed_trips = Trip.query.filter_by(
        status="COMPLETED"
    ).count()

    cancelled_trips = Trip.query.filter_by(
        status="CANCELLED"
    ).count()

    present_students = AttendanceRecord.query.filter_by(
        status="PRESENT"
    ).count()

    left_students = AttendanceRecord.query.filter_by(
        status="LEFT"
    ).count()

    not_detected_students = AttendanceRecord.query.filter_by(
        status="NOT_DETECTED"
    ).count()

    open_sos = SOSEvent.query.filter_by(
        status="OPEN"
    ).count()

    return {
        "students": {
            "active": total_students
        },

        "fleet": {
            "active_buses": total_buses,
            "active_drivers": total_drivers
        },

        "trips": {
            "active": active_trips,
            "planned": planned_trips,
            "completed": completed_trips,
            "cancelled": cancelled_trips
        },

        "attendance": {
            "present": present_students,
            "left": left_students,
            "not_detected": not_detected_students
        },

        "alerts": {
            "open_sos": open_sos
        }
    }