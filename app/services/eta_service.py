from datetime import datetime
from statistics import median
from math import radians, sin, cos, sqrt, atan2

from app.extensions import db
from app.models.trip import Trip
from app.models.gps_location import GPSLocation
from app.models.boarding_point import BoardingPoint


# =========================================================
# CONFIGURATION
# =========================================================

MIN_SPEED_KMH = 8.0
DEFAULT_SPEED_KMH = 20.0
MAX_REASONABLE_SPEED_KMH = 100.0

GPS_ACCURACY_LIMIT_M = 100.0

# GPS should normally be reasonably fresh.
MAX_GPS_AGE_SECONDS = 180

# Minimum historical trips required before using
# historical segment information confidently.
MIN_HISTORY_SAMPLES = 3

# Maximum amount of current delay that can affect ETA.
MAX_DELAY_ADJUSTMENT_MINUTES = 15.0

# How strongly current delay affects remaining ETA.
DELAY_WEIGHT = 0.50

# How much current-speed estimate contributes when
# historical segment information is available.
CURRENT_SPEED_WEIGHT = 0.30

# Historical estimate gets the remaining weight.
HISTORICAL_WEIGHT = 0.70

# Maximum accepted segment travel time.
MAX_SEGMENT_MINUTES = 180.0

# Ignore GPS jumps requiring impossible movement.
MAX_GPS_JUMP_KMH = 120.0


# =========================================================
# DISTANCE
# =========================================================

def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate straight-line distance between two coordinates.
    """

    earth_radius_km = 6371.0088

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


# =========================================================
# SPEED
# =========================================================

def get_safe_speed(speed_kmh):
    """
    Sanitize GPS speed.

    We never allow zero/negative/absurd speeds to
    directly produce an unrealistic ETA.
    """

    if speed_kmh is None:
        return DEFAULT_SPEED_KMH

    try:
        speed = float(speed_kmh)
    except (TypeError, ValueError):
        return DEFAULT_SPEED_KMH

    if speed < 0:
        return DEFAULT_SPEED_KMH

    if speed > MAX_REASONABLE_SPEED_KMH:
        return DEFAULT_SPEED_KMH

    if speed < MIN_SPEED_KMH:
        return MIN_SPEED_KMH

    return speed


# =========================================================
# GPS HISTORY
# =========================================================

def get_trip_gps_history(trip_id):
    """
    Return GPS points in chronological order.
    """

    return (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.asc())
        .all()
    )


# =========================================================
# VALID GPS
# =========================================================

def is_valid_gps(gps):
    """
    Reject GPS readings with poor accuracy.
    """

    if gps.accuracy_m is not None:
        try:
            if float(gps.accuracy_m) > GPS_ACCURACY_LIMIT_M:
                return False
        except (TypeError, ValueError):
            return False

    return True


# =========================================================
# GPS AGE
# =========================================================

def gps_age_seconds(gps):
    """
    Calculate how old the latest GPS reading is.
    """

    if not gps or not gps.recorded_at:
        return None

    now = datetime.utcnow()

    return max(
        0.0,
        (now - gps.recorded_at).total_seconds()
    )


# =========================================================
# CURRENT MOVEMENT SPEED
# =========================================================

def calculate_recent_speed(gps_history):
    """
    Estimate recent movement speed from the last valid
    GPS samples.

    This prevents one abnormal GPS speed reading from
    dominating the ETA.
    """

    valid_points = [
        gps for gps in gps_history
        if is_valid_gps(gps)
    ]

    if len(valid_points) < 2:
        return None

    recent = valid_points[-6:]

    calculated_speeds = []

    for previous, current in zip(recent, recent[1:]):

        seconds = (
            current.recorded_at
            - previous.recorded_at
        ).total_seconds()

        if seconds <= 0:
            continue

        distance_km = haversine_km(
            previous.latitude,
            previous.longitude,
            current.latitude,
            current.longitude
        )

        hours = seconds / 3600.0

        if hours <= 0:
            continue

        speed = distance_km / hours

        if 0 <= speed <= MAX_GPS_JUMP_KMH:
            calculated_speeds.append(speed)

    if not calculated_speeds:
        return None

    return median(calculated_speeds)


# =========================================================
# FINAL CURRENT SPEED
# =========================================================

def determine_current_speed(latest_gps, gps_history):
    """
    Combine the GPS-reported speed and recent movement speed.

    Recent movement is used to reduce dependence on one
    noisy GPS speed reading.
    """

    recent_speed = calculate_recent_speed(gps_history)

    gps_speed = None

    if latest_gps.speed_kmh is not None:
        try:
            value = float(latest_gps.speed_kmh)

            if 0 <= value <= MAX_REASONABLE_SPEED_KMH:
                gps_speed = value
        except (TypeError, ValueError):
            gps_speed = None

    if gps_speed is not None and recent_speed is not None:

        # Weighted combination.
        combined = (
            gps_speed * 0.40
            + recent_speed * 0.60
        )

        return get_safe_speed(combined), "GPS_SPEED + RECENT_MOVEMENT"

    if recent_speed is not None:
        return get_safe_speed(recent_speed), "RECENT_MOVEMENT"

    return get_safe_speed(gps_speed), "GPS_SPEED/FALLBACK"


# =========================================================
# SPEED ETA
# =========================================================

def calculate_speed_eta(distance_km, speed_kmh):

    if distance_km <= 0:
        return 0.0

    speed = get_safe_speed(speed_kmh)

    return (
        distance_km / speed
    ) * 60.0


# =========================================================
# STOP ARRIVAL
# =========================================================

def find_stop_arrival_time(gps_points, boarding_point):
    """
    Find the first valid GPS point entering the stop geofence.
    """

    radius_km = (
        float(boarding_point.geofence_radius_m or 200)
        / 1000.0
    )

    for gps in gps_points:

        if not is_valid_gps(gps):
            continue

        distance = haversine_km(
            gps.latitude,
            gps.longitude,
            boarding_point.latitude,
            boarding_point.longitude
        )

        if distance <= radius_km:
            return gps.recorded_at

    return None


# =========================================================
# HISTORICAL STOP ARRIVALS
# =========================================================

def get_historical_stop_arrivals(route_id):
    """
    Build historical arrival information:

        stop_order -> [arrival times from completed trips]

    Only completed trips with usable GPS history are used.
    """

    boarding_points = (
        BoardingPoint.query
        .filter_by(route_id=route_id)
        .order_by(BoardingPoint.stop_order.asc())
        .all()
    )

    completed_trips = (
        Trip.query
        .filter(
            Trip.route_id == route_id,
            Trip.status == "COMPLETED",
            Trip.start_time.isnot(None),
            Trip.end_time.isnot(None)
        )
        .all()
    )

    arrivals = {
        point.stop_order: []
        for point in boarding_points
    }

    for old_trip in completed_trips:

        gps_history = get_trip_gps_history(old_trip.id)

        if not gps_history:
            continue

        for point in boarding_points:

            arrival = find_stop_arrival_time(
                gps_history,
                point
            )

            if arrival:
                arrivals[point.stop_order].append(
                    arrival
                )

    return arrivals


# =========================================================
# HISTORICAL SEGMENT TIMES
# =========================================================

def get_historical_segment_data(route_id):
    """
    Calculate historical travel time for every consecutive
    route segment.

    Example:

        Stop 1 -> Stop 2
        Stop 2 -> Stop 3
        Stop 3 -> Stop 4
    """

    boarding_points = (
        BoardingPoint.query
        .filter_by(route_id=route_id)
        .order_by(BoardingPoint.stop_order.asc())
        .all()
    )

    if len(boarding_points) < 2:
        return {}

    completed_trips = (
        Trip.query
        .filter(
            Trip.route_id == route_id,
            Trip.status == "COMPLETED",
            Trip.start_time.isnot(None),
            Trip.end_time.isnot(None)
        )
        .all()
    )

    segments = {}

    for index in range(len(boarding_points) - 1):

        first = boarding_points[index]
        second = boarding_points[index + 1]

        segments[
            (first.stop_order, second.stop_order)
        ] = []

    for old_trip in completed_trips:

        gps_history = get_trip_gps_history(old_trip.id)

        if not gps_history:
            continue

        arrival_times = {}

        for point in boarding_points:

            arrival = find_stop_arrival_time(
                gps_history,
                point
            )

            if arrival:
                arrival_times[
                    point.stop_order
                ] = arrival

        for index in range(len(boarding_points) - 1):

            first = boarding_points[index]
            second = boarding_points[index + 1]

            first_time = arrival_times.get(
                first.stop_order
            )

            second_time = arrival_times.get(
                second.stop_order
            )

            if not first_time or not second_time:
                continue

            minutes = (
                second_time - first_time
            ).total_seconds() / 60.0

            if (
                minutes > 0
                and minutes <= MAX_SEGMENT_MINUTES
            ):
                segments[
                    (first.stop_order, second.stop_order)
                ].append(minutes)

    return segments


# =========================================================
# HISTORICAL REMAINING ETA
# =========================================================

def calculate_historical_remaining_eta(
    route_id,
    from_order,
    target_order
):
    """
    Calculate historical ETA from one route stop to another.

    Uses the median of each segment rather than the average,
    making the calculation more resistant to abnormal trips.
    """

    if target_order <= from_order:
        return 0.0, 0

    segment_data = get_historical_segment_data(
        route_id
    )

    total = 0.0
    sample_counts = []

    for order in range(
        from_order,
        target_order
    ):

        key = (
            order,
            order + 1
        )

        values = segment_data.get(key, [])

        if not values:
            return None, 0

        segment_median = median(values)

        total += segment_median
        sample_counts.append(len(values))

    if not sample_counts:
        return None, 0

    return total, min(sample_counts)


# =========================================================
# HISTORICAL ELAPSED TIME TO STOP
# =========================================================

def calculate_historical_elapsed_to_stop(
    route_id,
    stop_order
):
    """
    Historical median travel time from trip start to a
    particular stop.

    This is used to calculate CURRENT TRIP DELAY correctly.
    """

    boarding_points = (
        BoardingPoint.query
        .filter_by(route_id=route_id)
        .order_by(BoardingPoint.stop_order.asc())
        .all()
    )

    target = None

    for point in boarding_points:

        if point.stop_order == stop_order:
            target = point
            break

    if not target:
        return None, 0

    completed_trips = (
        Trip.query
        .filter(
            Trip.route_id == route_id,
            Trip.status == "COMPLETED",
            Trip.start_time.isnot(None),
            Trip.end_time.isnot(None)
        )
        .all()
    )

    values = []

    for old_trip in completed_trips:

        gps_history = get_trip_gps_history(
            old_trip.id
        )

        if not gps_history:
            continue

        arrival = find_stop_arrival_time(
            gps_history,
            target
        )

        if not arrival:
            continue

        elapsed = (
            arrival - old_trip.start_time
        ).total_seconds() / 60.0

        if 0 < elapsed <= 180:
            values.append(elapsed)

    if not values:
        return None, 0

    return median(values), len(values)


# =========================================================
# CURRENT ROUTE PROGRESS
# =========================================================

def find_current_anchor_stop(
    trip_id,
    boarding_points
):
    """
    Find the latest boarding point reached during the
    current trip.
    """

    gps_history = get_trip_gps_history(
        trip_id
    )

    if not gps_history:
        return boarding_points[0].stop_order

    reached = []

    for point in boarding_points:

        radius_km = (
            float(point.geofence_radius_m or 200)
            / 1000.0
        )

        for gps in gps_history:

            if not is_valid_gps(gps):
                continue

            distance = haversine_km(
                gps.latitude,
                gps.longitude,
                point.latitude,
                point.longitude
            )

            if distance <= radius_km:

                reached.append(
                    point.stop_order
                )

                break

    if reached:
        return max(reached)

    return boarding_points[0].stop_order


# =========================================================
# CURRENT DELAY
# =========================================================

def calculate_current_delay(
    trip,
    anchor_order
):
    """
    Calculate current trip delay correctly.

    Actual elapsed time is compared against the historical
    median elapsed time required to reach the current anchor.
    """

    if not trip.start_time:
        return 0.0, 0

    historical_elapsed, samples = (
        calculate_historical_elapsed_to_stop(
            trip.route_id,
            anchor_order
        )
    )

    if historical_elapsed is None:
        return 0.0, 0

    actual_elapsed = (
        datetime.utcnow()
        - trip.start_time
    ).total_seconds() / 60.0

    delay = (
        actual_elapsed
        - historical_elapsed
    )

    delay = max(
        -MAX_DELAY_ADJUSTMENT_MINUTES,
        min(
            delay,
            MAX_DELAY_ADJUSTMENT_MINUTES
        )
    )

    return delay, samples


# =========================================================
# FIND TARGET
# =========================================================

def find_target_boarding_point(
    trip,
    boarding_points,
    latest_gps,
    target_boarding_point_id
):

    if target_boarding_point_id:

        target = db.session.get(
            BoardingPoint,
            target_boarding_point_id
        )

        if not target:
            return None, "Target boarding point not found"

        if target.route_id != trip.route_id:
            return (
                None,
                "Boarding point does not belong to this route"
            )

        return target, None

    # If no target supplied, select the nearest
    # boarding point that has not already been passed.

    current_anchor = find_current_anchor_stop(
        trip.id,
        boarding_points
    )

    future_points = [
        point
        for point in boarding_points
        if point.stop_order >= current_anchor
    ]

    if not future_points:
        return None, "No upcoming boarding point"

    nearest = min(
        future_points,
        key=lambda point: haversine_km(
            latest_gps.latitude,
            latest_gps.longitude,
            point.latitude,
            point.longitude
        )
    )

    return nearest, None


# =========================================================
# MAIN ETA
# =========================================================

def calculate_eta(
    trip_id,
    target_boarding_point_id=None
):
    """
    Main SmartBus ETA engine.

    ETA uses:

    - latest GPS
    - GPS accuracy
    - recent movement
    - current speed
    - route progress
    - target boarding point
    - historical segment travel times
    - historical current-position delay
    - conservative delay adjustment

    It never claims higher confidence than the available
    historical data supports.
    """

    # -----------------------------------------------------
    # TRIP
    # -----------------------------------------------------

    trip = db.session.get(
        Trip,
        trip_id
    )

    if not trip:
        return {
            "success": False,
            "error": "Trip not found"
        }

    # -----------------------------------------------------
    # LATEST GPS
    # -----------------------------------------------------

    latest_gps = (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(
            GPSLocation.recorded_at.desc()
        )
        .first()
    )

    if not latest_gps:
        return {
            "success": False,
            "error": "No GPS location available"
        }

    if not is_valid_gps(latest_gps):

        return {
            "success": False,
            "error": (
                "Latest GPS accuracy is too poor "
                "for reliable ETA"
            ),
            "gps_accuracy_m": (
                float(latest_gps.accuracy_m)
                if latest_gps.accuracy_m is not None
                else None
            )
        }

    # -----------------------------------------------------
    # GPS FRESHNESS
    # -----------------------------------------------------

    age = gps_age_seconds(
        latest_gps
    )

    gps_status = "FRESH"

    if age is not None:

        if age > MAX_GPS_AGE_SECONDS:

            gps_status = "STALE"

    # -----------------------------------------------------
    # ROUTE
    # -----------------------------------------------------

    boarding_points = (
        BoardingPoint.query
        .filter_by(route_id=trip.route_id)
        .order_by(
            BoardingPoint.stop_order.asc()
        )
        .all()
    )

    if not boarding_points:

        return {
            "success": False,
            "error": "No boarding points found"
        }

    # -----------------------------------------------------
    # CURRENT ANCHOR
    # -----------------------------------------------------

    anchor_order = find_current_anchor_stop(
        trip_id,
        boarding_points
    )

    # -----------------------------------------------------
    # TARGET
    # -----------------------------------------------------

    target, target_error = (
        find_target_boarding_point(
            trip,
            boarding_points,
            latest_gps,
            target_boarding_point_id
        )
    )

    if not target:

        return {
            "success": False,
            "error": target_error
        }

    # -----------------------------------------------------
    # ARRIVED?
    # -----------------------------------------------------

    target_radius_km = (
        float(target.geofence_radius_m or 200)
        / 1000.0
    )

    direct_distance_km = haversine_km(
        latest_gps.latitude,
        latest_gps.longitude,
        target.latitude,
        target.longitude
    )

    if direct_distance_km <= target_radius_km:

        return {
            "success": True,
            "trip_id": trip_id,
            "eta": {
                "minutes": 0,
                "status": "ARRIVED",
                "boarding_point": target.name,
                "boarding_point_id": target.id,
                "stop_order": target.stop_order,
                "distance_km": round(
                    direct_distance_km,
                    3
                ),
                "confidence": "HIGH",
                "method": "GEOFENCE"
            }
        }

    # -----------------------------------------------------
    # CURRENT SPEED
    # -----------------------------------------------------

    gps_history = get_trip_gps_history(
        trip_id
    )

    current_speed, speed_method = (
        determine_current_speed(
            latest_gps,
            gps_history
        )
    )

    # -----------------------------------------------------
    # CURRENT DIRECT ETA
    # -----------------------------------------------------

    current_speed_eta = calculate_speed_eta(
        direct_distance_km,
        current_speed
    )

    # -----------------------------------------------------
    # HISTORICAL ETA
    # -----------------------------------------------------

    historical_eta = None
    historical_samples = 0

    if target.stop_order > anchor_order:

        (
            historical_eta,
            historical_samples
        ) = calculate_historical_remaining_eta(
            trip.route_id,
            anchor_order,
            target.stop_order
        )

    # -----------------------------------------------------
    # CURRENT DELAY
    # -----------------------------------------------------

    delay_minutes = 0.0
    delay_samples = 0

    if target.stop_order > anchor_order:

        (
            delay_minutes,
            delay_samples
        ) = calculate_current_delay(
            trip,
            anchor_order
        )

    # -----------------------------------------------------
    # FINAL ETA MODEL
    # -----------------------------------------------------

    if historical_eta is not None:

        # Historical route behaviour is the main estimate.
        base_eta = (
            historical_eta * HISTORICAL_WEIGHT
            +
            current_speed_eta * CURRENT_SPEED_WEIGHT
        )

        # Apply only a fraction of current delay.
        eta_minutes = (
            base_eta
            +
            delay_minutes * DELAY_WEIGHT
        )

        method = (
            "HISTORICAL_SEGMENTS"
            "+CURRENT_MOVEMENT"
            "+CURRENT_DELAY"
        )

        if historical_samples >= 10:
            confidence = "HIGH"

        elif historical_samples >= 5:
            confidence = "MEDIUM"

        else:
            confidence = "LOW"

    else:

        # No sufficient history.
        eta_minutes = current_speed_eta

        method = (
            "CURRENT_MOVEMENT_FALLBACK"
        )

        confidence = "LOW"

    # -----------------------------------------------------
    # GPS STALE PENALTY
    # -----------------------------------------------------

    if gps_status == "STALE":

        confidence = "LOW"

        method += "+STALE_GPS"

    # -----------------------------------------------------
    # FINAL LIMITS
    # -----------------------------------------------------

    eta_minutes = max(
        0.5,
        min(
            eta_minutes,
            180.0
        )
    )

    eta_minutes = round(
        eta_minutes,
        1
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "success": True,

        "trip_id": trip_id,

        "eta": {

            "minutes": eta_minutes,

            "status": "EN_ROUTE",

            "boarding_point": target.name,

            "boarding_point_id": target.id,

            "stop_order": target.stop_order,

            "current_anchor_stop_order": anchor_order,

            "distance_km": round(
                direct_distance_km,
                3
            ),

            "current_speed_kmh": round(
                current_speed,
                2
            ),

            "speed_method": speed_method,

            "historical_eta_minutes": (
                round(
                    historical_eta,
                    2
                )
                if historical_eta is not None
                else None
            ),

            "current_speed_eta_minutes": round(
                current_speed_eta,
                2
            ),

            "historical_samples": (
                historical_samples
            ),

            "delay_minutes": round(
                delay_minutes,
                2
            ),

            "delay_samples": (
                delay_samples
            ),

            "confidence": confidence,

            "method": method,

            "gps_source": (
                latest_gps.source
            ),

            "gps_age_seconds": (
                round(age, 1)
                if age is not None
                else None
            ),

            "gps_status": gps_status,

            "gps_accuracy_m": (
                round(
                    float(
                        latest_gps.accuracy_m
                    ),
                    2
                )
                if latest_gps.accuracy_m is not None
                else None
            ),

            "calculated_at": (
                datetime.utcnow().isoformat()
            )
        }
    }