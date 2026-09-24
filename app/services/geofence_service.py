from math import radians, sin, cos, sqrt, atan2

from app.models.boarding_point import BoardingPoint


DEFAULT_PROXIMITY_RADIUS_METERS = 300


def calculate_distance_meters(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate the distance between two GPS coordinates
    using the Haversine formula.
    """

    earth_radius_meters = 6371000

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

    return earth_radius_meters * c


def evaluate_proximity(
    latitude,
    longitude,
    boarding_point_id,
    radius_meters=DEFAULT_PROXIMITY_RADIUS_METERS
):
    """
    Determine whether the bus is inside the proximity
    geofence of a boarding point.
    """

    boarding_point = BoardingPoint.query.get(
        boarding_point_id
    )

    if not boarding_point:
        return {
            "available": False,
            "reason": "Boarding point not found"
        }

    distance_meters = calculate_distance_meters(
        latitude,
        longitude,
        boarding_point.latitude,
        boarding_point.longitude
    )

    is_nearby = distance_meters <= radius_meters

    return {
        "available": True,
        "boarding_point_id": boarding_point.id,
        "boarding_point_name": boarding_point.name,
        "distance_meters": round(distance_meters, 2),
        "radius_meters": radius_meters,
        "is_nearby": is_nearby
    }