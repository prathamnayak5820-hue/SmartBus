from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

from app.models.trip import Trip
from app.models.gps_location import GPSLocation
from app.models.boarding_point import BoardingPoint


DEFAULT_SPEED_KMH = 25.0
MIN_SPEED_KMH = 5.0
MAX_SPEED_KMH = 80.0


def calculate_distance_km(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate approximate distance between two GPS coordinates
    using the Haversine formula.
    """

    earth_radius_km = 6371.0

    lat1 = radians(latitude1)
    lat2 = radians(latitude2)

    delta_lat = radians(latitude2 - latitude1)
    delta_lon = radians(longitude2 - longitude1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


def get_latest_gps(trip_id):
    """
    Get the most recent GPS location for a trip.
    """

    return (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.desc())
        .first()
    )


def calculate_eta_to_boarding_point(
    trip_id,
    boarding_point_id
):
    """
    Calculate approximate ETA from the latest bus GPS
    location to a boarding point.

    The boarding point must belong to the route assigned
    to the specified trip.
    """

    trip = Trip.query.get(trip_id)

    if not trip:
        return {
            "available": False,
            "reason": "Trip not found"
        }

    boarding_point = BoardingPoint.query.get(
        boarding_point_id
    )

    if not boarding_point:
        return {
            "available": False,
            "reason": "Boarding point not found"
        }

    if str(boarding_point.route_id) != str(trip.route_id):
        return {
            "available": False,
            "reason": "Boarding point does not belong to trip route"
        }

    location = get_latest_gps(trip_id)

    if not location:
        return {
            "available": False,
            "reason": "No GPS location available"
        }

    distance_km = calculate_distance_km(
        location.latitude,
        location.longitude,
        boarding_point.latitude,
        boarding_point.longitude
    )

    # -----------------------------------------------------
    # Determine speed
    # -----------------------------------------------------

    speed_kmh = location.speed_kmh

    if speed_kmh is None:
        speed_kmh = DEFAULT_SPEED_KMH

    # Ignore unrealistic GPS speed values.
    speed_kmh = max(
        MIN_SPEED_KMH,
        min(speed_kmh, MAX_SPEED_KMH)
    )

    # -----------------------------------------------------
    # ETA calculation
    # -----------------------------------------------------

    travel_hours = distance_km / speed_kmh

    eta_minutes = travel_hours * 60

    eta_minutes = max(
        0,
        round(eta_minutes)
    )

    estimated_arrival = datetime.utcnow() + timedelta(
        minutes=eta_minutes
    )

    return {
        "available": True,
        "trip_id": trip.id,
        "route_id": trip.route_id,
        "boarding_point_id": boarding_point.id,
        "boarding_point_name": boarding_point.name,
        "distance_km": round(distance_km, 2),
        "speed_kmh": round(speed_kmh, 2),
        "eta_minutes": eta_minutes,
        "estimated_arrival": estimated_arrival.isoformat(),
        "gps_source": location.source,
        "gps_recorded_at": location.recorded_at.isoformat()
    }