from app.models.trip import Trip
from app.models.gps_location import GPSLocation
from app.models.attendance_record import AttendanceRecord


def get_live_trip_data(trip_id):
    trip = Trip.query.get(trip_id)

    if not trip:
        return None

    latest_gps = (
        GPSLocation.query
        .filter_by(trip_id=trip_id)
        .order_by(GPSLocation.recorded_at.desc())
        .first()
    )

    attendance_records = AttendanceRecord.query.filter_by(
        trip_id=trip_id
    ).all()

    passenger_count = sum(
        1 for record in attendance_records
        if record.status == "PRESENT"
    )

    bus = trip.bus

    return {
        "trip_id": trip.id,
        "status": trip.status,

        "bus": {
            "id": bus.id if bus else None,
            "bus_number": bus.bus_number if bus else None,
            "capacity": bus.capacity if bus else None,
        },

        "passengers": {
            "present": passenger_count,
            "capacity": bus.capacity if bus else None,
            "available_seats": (
                max(bus.capacity - passenger_count, 0)
                if bus else None
            ),
        },

        "location": {
            "available": latest_gps is not None,
            "latitude": latest_gps.latitude if latest_gps else None,
            "longitude": latest_gps.longitude if latest_gps else None,
            "speed_kmh": latest_gps.speed_kmh if latest_gps else None,
            "accuracy_m": latest_gps.accuracy_m if latest_gps else None,
            "source": latest_gps.source if latest_gps else None,
            "recorded_at": (
                latest_gps.recorded_at.isoformat()
                if latest_gps else None
            ),
        }
    }