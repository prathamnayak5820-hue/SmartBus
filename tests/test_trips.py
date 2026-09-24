def test_create_trip(client):
    # Register admin
    register_admin = client.post(
        "/api/auth/register",
        json={
            "name": "Trip Admin",
            "phone": "9999999996",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_admin.status_code == 201

    # Login admin
    login_admin = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999996",
            "password": "admin123"
        }
    )

    assert login_admin.status_code == 200
    admin_token = login_admin.get_json()["access_token"]

    # Create bus
    bus_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "bus_number": "TEST-BUS-01",
            "capacity": 40
        }
    )

    assert bus_response.status_code == 201
    bus_id = bus_response.get_json()["bus"]["id"]

    # Create route
    route_response = client.post(
        "/api/routes/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "name": "Trip Test Route",
            "description": "Route for trip testing"
        }
    )

    assert route_response.status_code == 201
    route_id = route_response.get_json()["route"]["id"]

    # Register driver
    register_driver = client.post(
        "/api/auth/register",
        json={
            "name": "Trip Driver",
            "phone": "9999999995",
            "password": "driver123",
            "role": "DRIVER"
        }
    )

    assert register_driver.status_code == 201
    
    login_driver = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999995",
            "password": "driver123"
        }
    )

    assert login_driver.status_code == 200

    driver_id = login_driver.get_json()["user"]["id"]
    # Create trip
    trip_response = client.post(
        "/api/trips/",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "bus_id": bus_id,
            "route_id": route_id,
            "driver_id": driver_id
        }
    )

    assert trip_response.status_code == 201

    trip_data = trip_response.get_json()["trip"]

    assert trip_data["bus_id"] == bus_id
    assert trip_data["route_id"] == route_id
    assert trip_data["driver_id"] == driver_id
    assert trip_data["status"] == "PLANNED"