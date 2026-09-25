def test_bus_health(client):
    response = client.get("/api/buses/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Bus routes are working"
    assert data["status"] == "success"


def test_create_bus(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Bus Admin",
            "phone": "9999999994",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999994",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "TEST-BUS-02",
            "capacity": 40
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Bus created successfully"
    assert data["bus"]["bus_number"] == "TEST-BUS-02"
    assert data["bus"]["capacity"] == 40
    assert data["bus"]["is_active"] is True

def test_list_buses(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "List Bus Admin",
            "phone": "9999999993",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999993",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    create_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "TEST-BUS-03",
            "capacity": 50
        }
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert any(
        bus["bus_number"] == "TEST-BUS-03"
        for bus in data
    )
def test_get_bus(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Get Bus Admin",
            "phone": "9999999992",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999992",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    create_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "TEST-BUS-04",
            "capacity": 45
        }
    )

    assert create_response.status_code == 201

    bus_id = create_response.get_json()["bus"]["id"]

    response = client.get(
        f"/api/buses/{bus_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == bus_id
    assert data["bus_number"] == "TEST-BUS-04"
    assert data["capacity"] == 45
    assert data["is_active"] is True

def test_assign_driver(client):
    register_admin = client.post(
        "/api/auth/register",
        json={
            "name": "Assign Admin",
            "phone": "9999999991",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_admin.status_code == 201

    login_admin = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999991",
            "password": "admin123"
        }
    )

    assert login_admin.status_code == 200
    token = login_admin.get_json()["access_token"]

    create_bus = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "TEST-BUS-05",
            "capacity": 40
        }
    )

    assert create_bus.status_code == 201
    bus_id = create_bus.get_json()["bus"]["id"]

    register_driver = client.post(
        "/api/auth/register",
        json={
            "name": "Bus Driver",
            "phone": "9999999990",
            "password": "driver123",
            "role": "DRIVER"
        }
    )

    assert register_driver.status_code == 201

    login_driver = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999990",
            "password": "driver123"
        }
    )

    assert login_driver.status_code == 200
    driver_id = login_driver.get_json()["user"]["id"]

    response = client.patch(
        f"/api/buses/{bus_id}/assign-driver",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "driver_id": driver_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Driver assigned successfully"
    assert data["bus_id"] == bus_id
    assert data["driver_id"] == driver_id

def test_create_duplicate_bus(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Duplicate Bus Admin",
            "phone": "9999999989",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999989",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    first_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "DUPLICATE-BUS",
            "capacity": 40
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "DUPLICATE-BUS",
            "capacity": 40
        }
    )

    assert second_response.status_code == 409

    data = second_response.get_json()

    assert data["error"] == "Bus number already exists"


def test_student_cannot_create_bus(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Bus Student",
            "phone": "9999999988",
            "password": "student123",
            "role": "STUDENT"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999988",
            "password": "student123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "UNAUTHORIZED-BUS",
            "capacity": 40
        }
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "Only admin or college can create buses"

def test_assign_nonexistent_driver(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Driver Assign Admin",
            "phone": "9999999987",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999987",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    create_bus_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "NO-DRIVER-BUS",
            "capacity": 40
        }
    )

    assert create_bus_response.status_code == 201

    bus_id = create_bus_response.get_json()["bus"]["id"]

    response = client.patch(
        f"/api/buses/{bus_id}/assign-driver",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "driver_id": "non-existent-driver-id"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Driver not found"

def test_assign_nonexistent_driver(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Driver Assign Admin",
            "phone": "9999999987",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999987",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    create_bus_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "NO-DRIVER-BUS",
            "capacity": 40
        }
    )

    assert create_bus_response.status_code == 201

    bus_id = create_bus_response.get_json()["bus"]["id"]

    response = client.patch(
        f"/api/buses/{bus_id}/assign-driver",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "driver_id": "non-existent-driver-id"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Driver not found"

def test_get_nonexistent_bus(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Get Bus Admin",
            "phone": "9999999985",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999985",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/buses/non-existent-bus-id",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Bus not found"

def test_assign_student_as_driver(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Assign Admin",
            "phone": "9999999984",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999984",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    student_response = client.post(
        "/api/auth/register",
        json={
            "name": "Not A Driver",
            "phone": "9999999983",
            "password": "student123",
            "role": "STUDENT"
        }
    )

    assert student_response.status_code == 201

    student_login = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999983",
            "password": "student123"
        }
    )

    assert student_login.status_code == 200
    student_id = student_login.get_json()["user"]["id"]

    create_bus_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "WRONG-DRIVER-BUS",
            "capacity": 40
        }
    )

    assert create_bus_response.status_code == 201

    bus_id = create_bus_response.get_json()["bus"]["id"]

    response = client.patch(
        f"/api/buses/{bus_id}/assign-driver",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "driver_id": student_id
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "User is not a driver"

def test_assign_driver_missing_id(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Missing Driver Admin",
            "phone": "9999999982",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999982",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    create_bus_response = client.post(
        "/api/buses/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "bus_number": "MISSING-DRIVER-BUS",
            "capacity": 40
        }
    )

    assert create_bus_response.status_code == 201

    bus_id = create_bus_response.get_json()["bus"]["id"]

    response = client.patch(
        f"/api/buses/{bus_id}/assign-driver",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "driver_id is required"
def test_list_students(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Student List Admin",
            "phone": "9999999981",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999981",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_list_students(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Student List Admin",
            "phone": "9999999981",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999981",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)