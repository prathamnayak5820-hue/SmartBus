from datetime import datetime, timedelta

from app.extensions import db
from app.models.attendance_record import AttendanceRecord


PRESENCE_TIMEOUT_SECONDS = 60


def process_presence_event(presence_event, commit=True):
    """
    Process a BLE presence event and update attendance.

    commit=True:
        Used by the normal single-event API.

    commit=False:
        Used by offline synchronization so the entire
        batch can be committed together.
    """

    attendance = AttendanceRecord.query.filter_by(
        trip_id=presence_event.trip_id,
        student_id=presence_event.student_id
    ).first()

    if not attendance:
        attendance = AttendanceRecord(
            trip_id=presence_event.trip_id,
            student_id=presence_event.student_id,
            status="UNKNOWN"
        )
        db.session.add(attendance)

    event_time = presence_event.detected_at or datetime.utcnow()

    if presence_event.event_type == "DETECTED":

        if attendance.first_seen is None:
            attendance.first_seen = event_time

        attendance.last_seen = event_time
        attendance.status = "PRESENT"
        attendance.left_at = None

    elif presence_event.event_type == "LEFT":

        attendance.last_seen = event_time
        attendance.left_at = event_time
        attendance.status = "LEFT"

    attendance.updated_at = datetime.utcnow()

    if commit:
        db.session.commit()

    return attendance


def mark_timed_out_attendance(trip_id):
    """
    Mark PRESENT students as NOT_DETECTED when
    their last BLE detection exceeds the timeout.
    """

    now = datetime.utcnow()

    timeout_limit = now - timedelta(
        seconds=PRESENCE_TIMEOUT_SECONDS
    )

    records = AttendanceRecord.query.filter(
        AttendanceRecord.trip_id == trip_id,
        AttendanceRecord.status == "PRESENT",
        AttendanceRecord.last_seen < timeout_limit
    ).all()

    updated_records = []

    for attendance in records:

        attendance.status = "NOT_DETECTED"
        attendance.left_at = now
        attendance.updated_at = now

        updated_records.append(attendance)

    db.session.commit()

    return updated_records