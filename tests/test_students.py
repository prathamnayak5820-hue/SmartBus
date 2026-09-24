def test_create_student(client):
    # Register admin
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Test Admin",
            "phone": "9999999998",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    # Login admin
    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999998",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    # Create student
    response = client.post(
        "/api/students/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Student",
            "usn": "TEST001",
            "phone": "8888888888"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["student"]["name"] == "Test Student"
    assert data["student"]["usn"] == "TEST001"
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
        "/api/students/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    data = response.get_json()

    assert "students" in data
    assert isinstance(data["students"], list)

def test_get_student(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Get Student Admin",
            "phone": "9999999980",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999980",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    create_response = client.post(
        "/api/students/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Single Student",
            "usn": "GET001",
            "phone": "8888888880"
        }
    )

    assert create_response.status_code == 201

    student_id = create_response.get_json()["student"]["id"]

    response = client.get(
        f"/api/students/{student_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == student_id
    assert data["name"] == "Single Student"
    assert data["usn"] == "GET001"

def test_get_nonexistent_student(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Missing Student Admin",
            "phone": "9999999979",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999979",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/students/999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Student not found"


def test_assign_student_to_bus(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Bus Assign Admin",
            "phone": "9999999978",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999978",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    # Create student
    student_response = client.post(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Bus Student",
            "usn": "BUS001",
            "phone": "8888888878"
        }
    )

    assert student_response.status_code == 201
    student_id = student_response.get_json()["student"]["id"]

    # Create bus
    bus_response = client.post(
        "/api/buses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "bus_number": "STUDENT-BUS-01",
            "capacity": 40
        }
    )

    assert bus_response.status_code == 201
    bus_id = bus_response.get_json()["bus"]["id"]

    # Assign bus
    response = client.patch(
        f"/api/students/{student_id}/bus",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "bus_id": bus_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()
    print(data)

def test_get_student_attendance(client):
    login_response = client.post(
    "/api/auth/login",
    json={
        "phone": "9999999981",
        "password": "admin123"
    }
)
    print(login_response.get_json())
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/students/1/attendance",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.get_json())

    assert response.status_code == 200