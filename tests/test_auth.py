def test_register_login_and_me(client):
    # 1. Register
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Pytest Student",
            "phone": "9999999999",
            "password": "test1234",
            "role": "STUDENT"
        }
    )

    assert register_response.status_code == 201

    # 2. Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "phone": "9999999999",
            "password": "test1234"
        }
    )

    assert login_response.status_code == 200

    login_data = login_response.get_json()

    assert "access_token" in login_data

    access_token = login_data["access_token"]

    # 3. Access /me using JWT
    me_response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert me_response.status_code == 200

    me_data = me_response.get_json()

    # 4. Verify user
    assert me_data["name"] == "Pytest Student"
    assert me_data["phone"] == "9999999999"
    assert me_data["role"] == "STUDENT"