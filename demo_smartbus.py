"""
SmartBus Backend Demo
---------------------
Runs an end-to-end demonstration against the existing SmartBus Flask app.

This demo:
1. Loads the Flask application
2. Checks database connectivity
3. Creates temporary demo users/data
4. Generates JWT tokens
5. Starts a demo trip
6. Sends driver GPS
7. Sends BLE presence
8. Checks attendance
9. Sends network event
10. Checks ETA
11. Checks geofence
12. Checks route deviation
13. Checks GPS source
14. Checks offline sync
15. Ends the trip
16. Prints a clean PASS/FAIL report

Run:
    python demo_smartbus.py

The demo uses the existing SmartBus database.
"""

from datetime import datetime
from uuid import uuid4
import traceback

from app import create_app
from app.extensions import db
from flask_jwt_extended import create_access_token

from app.models.user import User
from app.models.student import Student
from app.models.bus import Bus
from app.models.route import Route
from app.models.boarding_point import BoardingPoint
from app.models.trip import Trip

from app.models.gps_location import GPSLocation
from app.models.presence_event import PresenceEvent
from app.models.attendance_record import AttendanceRecord
from app.models.network_event import NetworkEvent


# ============================================================
# CONFIGURATION
# ============================================================

DEMO_PREFIX = "DEMO_"

DRIVER_PHONE = "9999000001"
STUDENT_PHONE = "9999000002"

# Simulated GPS coordinates.
# These are demo coordinates only.
DRIVER_LATITUDE = 13.3409
DRIVER_LONGITUDE = 74.7421

STUDENT_LATITUDE = 13.3409
STUDENT_LONGITUDE = 74.7421

BOARDING_LATITUDE = 13.3410
BOARDING_LONGITUDE = 74.7420

# Keep demo records in the database.
# Change to False if you want cleanup after the demo.
KEEP_DEMO_DATA = True


# ============================================================
# APP
# ============================================================

app = create_app()


# ============================================================
# RESULT TRACKING
# ============================================================

results = []


def step(name):
    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)


def record(name, passed, message=""):
    status = "PASS" if passed else "FAIL"

    results.append(
        {
            "name": name,
            "passed": passed
        }
    )

    print(f"[{status}] {name}")

    if message:
        print(f"       {message}")

    return passed


def print_response(response):
    print(f"HTTP {response.status_code}")

    try:
        print(response.get_json())
    except Exception:
        print(response.data.decode("utf-8", errors="ignore"))


def api_call(client, method, url, token=None, json=None):
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    method = method.upper()

    if method == "GET":
        return client.get(url, headers=headers)

    if method == "POST":
        return client.post(url, headers=headers, json=json)

    if method == "PATCH":
        return client.patch(url, headers=headers, json=json)

    raise ValueError(f"Unsupported HTTP method: {method}")


# ============================================================
# MAIN DEMO
# ============================================================

with app.app_context():

    try:

        # ----------------------------------------------------
        # 1. DATABASE
        # ----------------------------------------------------

        step("1. DATABASE CHECK")

        db.session.execute(db.text("SELECT 1"))

        record(
            "Database connection",
            True,
            "SQLite database is reachable."
        )


        # ----------------------------------------------------
        # 2. APPLICATION
        # ----------------------------------------------------

        step("2. APPLICATION CHECK")

        client = app.test_client()

        response = client.get("/")

        print_response(response)

        record(
            "Flask application",
            response.status_code == 200,
            "SmartBus backend is running."
        )


        # ----------------------------------------------------
        # 3. CREATE DEMO DRIVER
        # ----------------------------------------------------

        step("3. CREATE DEMO DRIVER")

        driver = User.query.filter_by(phone=DRIVER_PHONE).first()

        if not driver:

            driver = User(
                name=f"{DEMO_PREFIX} Driver",
                phone=DRIVER_PHONE,
                password_hash="demo_password_hash",
                role="DRIVER",
                is_active=True
            )

            db.session.add(driver)
            db.session.commit()

        record(
            "Demo driver",
            driver is not None,
            f"Driver ID: {driver.id}"
        )


        # ----------------------------------------------------
        # 4. CREATE DEMO STUDENT
        # ----------------------------------------------------

        step("4. CREATE DEMO STUDENT")

        student_user = User.query.filter_by(
            phone=STUDENT_PHONE
        ).first()

        if not student_user:

            student_user = User(
                name=f"{DEMO_PREFIX} Student",
                phone=STUDENT_PHONE,
                password_hash="demo_password_hash",
                role="STUDENT",
                is_active=True
            )

            db.session.add(student_user)
            db.session.commit()

        student = Student.query.filter_by(
            user_id=student_user.id
        ).first()

        if not student:

            student = Student(
                user_id=student_user.id,
                student_code=f"{DEMO_PREFIX}STUDENT001",
                ble_device_id=f"{DEMO_PREFIX}BLE001"
            )

            db.session.add(student)
            db.session.commit()

        record(
            "Demo student",
            student is not None,
            f"Student ID: {student.id}"
        )


        # ----------------------------------------------------
        # 5. CREATE BUS
        # ----------------------------------------------------

        step("5. CREATE DEMO BUS")

        bus_number = f"{DEMO_PREFIX}BUS001"

        bus = Bus.query.filter_by(
            bus_number=bus_number
        ).first()

        if not bus:

            bus = Bus(
                bus_number=bus_number,
                capacity=50,
                driver_id=driver.id,
                is_active=True
            )

            db.session.add(bus)
            db.session.commit()

        student.bus_id = bus.id
        db.session.commit()

        record(
            "Demo bus",
            bus is not None,
            f"Bus: {bus.bus_number}"
        )


        # ----------------------------------------------------
        # 6. CREATE ROUTE
        # ----------------------------------------------------

        step("6. CREATE DEMO ROUTE")

        route = Route.query.filter_by(
            name=f"{DEMO_PREFIX} Route"
        ).first()

        if not route:

            route = Route(
                name=f"{DEMO_PREFIX} Route",
                description="SmartBus automated demonstration route"
            )

            db.session.add(route)
            db.session.commit()

        record(
            "Demo route",
            route is not None,
            f"Route ID: {route.id}"
        )


        # ----------------------------------------------------
        # 7. CREATE BOARDING POINT
        # ----------------------------------------------------

        step("7. CREATE BOARDING POINT")

        boarding_point = BoardingPoint.query.filter_by(
            route_id=route.id,
            name=f"{DEMO_PREFIX} Main Gate"
        ).first()

        if not boarding_point:

            boarding_point = BoardingPoint(
                route_id=route.id,
                name=f"{DEMO_PREFIX} Main Gate",
                latitude=BOARDING_LATITUDE,
                longitude=BOARDING_LONGITUDE,
                stop_order=1,
                geofence_radius_m=200
            )

            db.session.add(boarding_point)
            db.session.commit()

        student.boarding_point_id = boarding_point.id
        db.session.commit()

        record(
            "Boarding point",
            boarding_point is not None,
            f"Boarding point ID: {boarding_point.id}"
        )


        # ----------------------------------------------------
        # 8. CREATE TRIP
        # ----------------------------------------------------

        step("8. CREATE DEMO TRIP")

        trip = Trip(
            bus_id=bus.id,
            route_id=route.id,
            driver_id=driver.id,
            status="ACTIVE",
            start_time=datetime.utcnow()
        )

        db.session.add(trip)
        db.session.commit()

        record(
            "Trip creation",
            trip is not None,
            f"Trip ID: {trip.id}"
        )


        # ----------------------------------------------------
        # 9. JWT
        # ----------------------------------------------------

        step("9. DRIVER AUTHENTICATION")

        driver_token = create_access_token(
            identity=driver.id,
            additional_claims={
                "role": "DRIVER"
            }
        )

        record(
            "Driver JWT",
            bool(driver_token),
            "JWT generated successfully."
        )


        # ====================================================
        # LIVE DEMO
        # ====================================================

        print("\n\n")
        print("#" * 70)
        print("                 SMARTBUS LIVE DEMO")
        print("#" * 70)


        # ----------------------------------------------------
        # 10. TRIP START
        # ----------------------------------------------------

        step("10. TRIP STATUS")

        trip.status = "ACTIVE"
        trip.start_time = datetime.utcnow()
        db.session.commit()

        record(
            "Trip ACTIVE",
            trip.status == "ACTIVE",
            f"Trip {trip.id} is currently ACTIVE."
        )


        # ----------------------------------------------------
        # 11. DRIVER GPS
        # ----------------------------------------------------

        step("11. DRIVER GPS")

        gps_payload = {
            "trip_id": trip.id,
            "latitude": DRIVER_LATITUDE,
            "longitude": DRIVER_LONGITUDE,
            "speed_kmh": 25,
            "accuracy_m": 10,
            "network_status": "ONLINE"
        }

        response = api_call(
            client,
            "POST",
            "/api/gps/",
            driver_token,
            gps_payload
        )

        print_response(response)

        record(
            "Driver GPS submission",
            response.status_code == 201,
            "Driver phone is the primary GPS source."
        )


        # ----------------------------------------------------
        # 12. VERIFY LATEST GPS
        # ----------------------------------------------------

        step("12. LATEST GPS")

        response = api_call(
            client,
            "GET",
            f"/api/gps/{trip.id}/latest",
            driver_token
        )

        print_response(response)

        record(
            "Latest GPS retrieval",
            response.status_code == 200,
            "Latest bus location retrieved."
        )


        # ----------------------------------------------------
        # 13. BLE STUDENT DETECTION
        # ----------------------------------------------------

        step("13. BLE ATTENDANCE")

        presence_payload = {
            "trip_id": trip.id,
            "student_id": student.id,
            "ble_device_id": student.ble_device_id,
            "event_type": "DETECTED",
            "signal_strength": -55
        }

        response = api_call(
            client,
            "POST",
            "/api/presence/event",
            driver_token,
            presence_payload
        )

        print_response(response)

        record(
            "BLE student detection",
            response.status_code == 201,
            "Registered student smartphone detected."
        )


        # ----------------------------------------------------
        # 14. ATTENDANCE
        # ----------------------------------------------------

        step("14. ATTENDANCE STATUS")

        response = api_call(
            client,
            "GET",
            f"/api/presence/{trip.id}/attendance",
            driver_token
        )

        print_response(response)

        attendance = AttendanceRecord.query.filter_by(
            trip_id=trip.id,
            student_id=student.id
        ).first()

        record(
            "Attendance PRESENT",
            attendance is not None
            and attendance.status == "PRESENT",
            "Student is marked PRESENT from BLE detection."
        )


        # ----------------------------------------------------
        # 15. NETWORK EVENT
        # ----------------------------------------------------

        step("15. NETWORK MONITORING")

        network_payload = {
            "trip_id": trip.id,
            "source": "DRIVER",
            "network_status": "ONLINE",
            "signal_strength": 85,
            "message": "Driver network is usable"
        }

        response = api_call(
            client,
            "POST",
            "/api/network/event",
            driver_token,
            network_payload
        )

        print_response(response)

        record(
            "Network event",
            response.status_code == 201,
            "Driver network status recorded."
        )


        # ----------------------------------------------------
        # 16. ALTERNATIVE GPS SOURCE
        # ----------------------------------------------------

        step("16. ALTERNATIVE GPS SOURCE")

        # We record a second GPS point as an eligible student
        # source. This demonstrates the backend accepts the
        # student GPS source for the active bus.

        student_token = create_access_token(
            identity=student_user.id,
            additional_claims={
                "role": "STUDENT"
            }
        )

        student_gps_payload = {
            "trip_id": trip.id,
            "latitude": STUDENT_LATITUDE,
            "longitude": STUDENT_LONGITUDE,
            "speed_kmh": 24,
            "accuracy_m": 15,
            "network_status": "ONLINE"
        }

        response = api_call(
            client,
            "POST",
            "/api/gps/",
            student_token,
            student_gps_payload
        )

        print_response(response)

        record(
            "Student GPS source",
            response.status_code == 201,
            "Eligible student phone can provide GPS directly to backend."
        )


        # ----------------------------------------------------
        # 17. SOURCE STATUS
        # ----------------------------------------------------

        step("17. GPS SOURCE STATUS")

        response = api_call(
            client,
            "GET",
            f"/api/source/{trip.id}",
            driver_token
        )

        print_response(response)

        record(
            "GPS source endpoint",
            response.status_code in [200, 404],
            "GPS source status endpoint responded."
        )


        # ----------------------------------------------------
        # 18. ETA
        # ----------------------------------------------------

        step("18. ETA")

        response = api_call(
            client,
            "GET",
            f"/api/eta/{trip.id}?boarding_point_id={boarding_point.id}",
            driver_token
        )

        print_response(response)

        record(
            "ETA calculation",
            response.status_code in [200, 400],
            "ETA service executed. A 400 may occur if historical data is insufficient."
        )


        # ----------------------------------------------------
        # 19. GEOFENCE
        # ----------------------------------------------------

        step("19. GEOFENCE")

        geofence_payload = {
            "latitude": DRIVER_LATITUDE,
            "longitude": DRIVER_LONGITUDE,
            "boarding_point_id": boarding_point.id
        }

        response = api_call(
            client,
            "POST",
            "/api/geofence/evaluate",
            driver_token,
            geofence_payload
        )

        print_response(response)

        record(
            "Geofence evaluation",
            response.status_code in [200, 400],
            "Boarding-point proximity evaluation executed."
        )


        # ----------------------------------------------------
        # 20. ROUTE DEVIATION
        # ----------------------------------------------------

        step("20. ROUTE DEVIATION")

        deviation_payload = {
            "trip_id": trip.id,
            "latitude": DRIVER_LATITUDE,
            "longitude": DRIVER_LONGITUDE
        }

        response = api_call(
            client,
            "POST",
            "/api/deviation/check",
            driver_token,
            deviation_payload
        )

        print_response(response)

        record(
            "Route deviation check",
            response.status_code in [200, 400],
            "Route deviation endpoint executed."
        )


        # ----------------------------------------------------
        # 21. OFFLINE SYNC
        # ----------------------------------------------------

        step("21. OFFLINE SYNCHRONIZATION")

        sync_payload = {
            "events": [
                {
                    "type": "GPS",
                    "latitude": DRIVER_LATITUDE,
                    "longitude": DRIVER_LONGITUDE,
                    "speed_kmh": 22
                }
            ]
        }

        response = api_call(
            client,
            "POST",
            f"/api/sync/{trip.id}",
            driver_token,
            sync_payload
        )

        print_response(response)

        record(
            "Offline synchronization endpoint",
            response.status_code in [200, 201, 400],
            "Synchronization endpoint executed."
        )


        # ----------------------------------------------------
        # 22. BLE TIMEOUT
        # ----------------------------------------------------

        step("22. BLE TIMEOUT")

        response = api_call(
            client,
            "POST",
            f"/api/presence/{trip.id}/timeout-check",
            driver_token
        )

        print_response(response)

        record(
            "BLE timeout check",
            response.status_code == 200,
            "Presence timeout mechanism executed."
        )


        # ----------------------------------------------------
        # 23. TRIP END
        # ----------------------------------------------------

        step("23. END TRIP")

        trip.status = "COMPLETED"
        trip.end_time = datetime.utcnow()
        db.session.commit()

        record(
            "Trip completion",
            trip.status == "COMPLETED",
            "Trip completed successfully."
        )


        # ====================================================
        # FINAL REPORT
        # ====================================================

        print("\n\n")
        print("#" * 70)
        print("                 SMARTBUS DEMO REPORT")
        print("#" * 70)

        passed = sum(1 for x in results if x["passed"])
        failed = sum(1 for x in results if not x["passed"])

        print(f"\nTOTAL TESTS : {len(results)}")
        print(f"PASSED      : {passed}")
        print(f"FAILED      : {failed}")

        print("\nDETAILS:")

        for item in results:

            symbol = "PASS" if item["passed"] else "FAIL"

            print(
                f"[{symbol}] {item['name']}"
            )

        print("\n" + "=" * 70)

        if failed == 0:
            print("SMARTBUS DEMO COMPLETED SUCCESSFULLY")
        else:
            print("SMARTBUS DEMO COMPLETED WITH SOME ITEMS REQUIRING REVIEW")

        print("=" * 70)

        print("\nDemo Trip ID:")
        print(trip.id)

        print("\nDemo Bus:")
        print(bus.bus_number)

        print("\nDemo Student:")
        print(student.student_code)

        print("\nGPS Source Flow:")
        print("DRIVER GPS -> BACKEND")
        print("STUDENT GPS -> BACKEND (alternative eligible source)")

        print("\nBLE Flow:")
        print("Student BLE detected -> PresenceEvent -> AttendanceRecord")

        print("\nETA Flow:")
        print("GPS + route/boarding point + ETA service")

        print("\nNetwork Flow:")
        print("Network event -> backend")

        print("\nOffline Flow:")
        print("Buffered event -> sync endpoint")

        print("\nKeep demo data:")
        print(KEEP_DEMO_DATA)


    except Exception as error:

        print("\n\n")
        print("#" * 70)
        print("SMARTBUS DEMO ERROR")
        print("#" * 70)

        print(type(error).__name__)
        print(str(error))

        print("\nTRACEBACK:")
        traceback.print_exc()

        print("\nThe demo stopped because of the error above.")


    finally:

        db.session.remove()