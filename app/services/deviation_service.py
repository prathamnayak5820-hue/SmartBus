from app.models.trip import Trip
from app.models.gps_location import GPSLocation
from app.models.boarding_point import BoardingPoint
from app.services.geofence_service import calculate_distance_meters


DEFAULT_DEVIATION_RADIUS_METERS = 500


def get_latest_location(trip_id):
    """
    Get the latest GPS location for the trip.
    """

    return (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.desc())
        .first()
    )


def get_route_boarding_points(trip):
    """
    Get active boarding points belonging only to
    the route assigned to this trip.
    """

    return (
        BoardingPoint.query
        .filter_by(
            route_id=trip.route_id,
            is_active=True
        )
        .order_by(BoardingPoint.stop_order.asc())
        .all()
    )


def evaluate_route_deviation(
    trip_id,
    deviation_radius_meters=DEFAULT_DEVIATION_RADIUS_METERS
):
    """
    Determine whether the latest bus GPS position is
    significantly away from the boarding points of
    the trip's assigned route.

    This is a simplified route-corridor check.
    """

    trip = Trip.query.get(trip_id)

    if not trip:
        return {
            "available": False,
            "reason": "Trip not found"
        }

    location = get_latest_location(trip_id)

    if not location:
        return {
            "available": False,
            "reason": "No GPS location available"
        }

    boarding_points = get_route_boarding_points(trip)

    if not boarding_points:
        return {
            "available": False,
            "reason": "No boarding points available for this route"
        }

    nearest_distance = None
    nearest_boarding_point = None

    for point in boarding_points:
        distance = calculate_distance_meters(
            location.latitude,
            location.longitude,
            point.latitude,
            point.longitude
        )

        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_boarding_point = point

    is_deviated = (
        nearest_distance > deviation_radius_meters
    )

    return {
        "available": True,
        "trip_id": trip.id,
        "route_id": trip.route_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "nearest_boarding_point_id": (
            nearest_boarding_point.id
            if nearest_boarding_point
            else None
        ),
        "nearest_boarding_point_name": (
            nearest_boarding_point.name
            if nearest_boarding_point
            else None
        ),
        "distance_from_route_meters": round(
            nearest_distance,
            2
        ),
        "deviation_radius_meters": deviation_radius_meters,
        "is_deviated": is_deviated
    }