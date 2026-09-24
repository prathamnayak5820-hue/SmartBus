def test_create_route(client):
    # Register admin
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Route Admin",
            "phone": "9999999997",
            "password": "admin123",
            "role": "ADMIN"
        }
    )

    assert register_response.status_code == 201

    # Login admin
    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999997",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    # Create route
    response = client.post(
        "/api/routes/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Route",
            "description": "Pytest route"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["route"]["name"] == "Test Route"
    assert data["route"]["description"] == "Pytest route"
    assert data["route"]["is_active"] is True