from datetime import datetime

from app.extensions import db
from app.models.sos_event import SOSEvent
from app.models.trip import Trip
from app.models.user import User


def create_sos_event(
    trip_id,
    driver_id,
    latitude=None,
    longitude=None,
    message=None
):
    """
    Create an emergency SOS event for an active trip.
    """

    trip = Trip.query.get(trip_id)

    if not trip:
        raise ValueError("Trip not found")

    if trip.status != "ACTIVE":
        raise ValueError(
            "SOS can only be created for an active trip"
        )

    if str(trip.driver_id) != str(driver_id):
        raise PermissionError(
            "Only the assigned driver can create SOS"
        )

    sos_event = SOSEvent(
        trip_id=trip.id,
        bus_id=trip.bus_id,
        driver_id=driver_id,
        latitude=latitude,
        longitude=longitude,
        message=message,
        status="OPEN",
        created_at=datetime.utcnow()
    )

    db.session.add(sos_event)
    db.session.commit()

    return sos_event


def resolve_sos_event(sos_event_id):
    """
    Mark an SOS event as resolved.
    """

    sos_event = SOSEvent.query.get(
        sos_event_id
    )

    if not sos_event:
        return None

    sos_event.status = "RESOLVED"
    sos_event.resolved_at = datetime.utcnow()

    db.session.commit()

    return sos_event


def get_active_sos_events():
    """
    Get all currently open SOS events.
    """

    return (
        SOSEvent.query
        .filter_by(status="OPEN")
        .order_by(SOSEvent.created_at.desc())
        .all()
    )


def get_sos_event(sos_event_id):
    """
    Get a single SOS event.
    """

    return SOSEvent.query.get(
        sos_event_id
    )