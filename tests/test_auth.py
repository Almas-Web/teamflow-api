import time


def unique_email(prefix):
    return f"{prefix}_{int(time.time() * 1000)}@gmail.com"


# ---------------- REGISTER 
def test_register_user(client):
    email = unique_email("almas")

    response = client.post("/users", json={
        "name": "Almas",
        "email": email,
        "password": "1234"
    })

    assert response.status_code in [200, 201]
    assert response.json()["email"] == email


# ---------------- LOGIN 
def test_login_user(client):
    email = unique_email("login")

    client.post("/users", json={
        "name": "Login Test",
        "email": email,
        "password": "123456"
    })

    response = client.post("/users/token", data={
        "username": email,
        "password": "123456"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


# ---------------- PROTECTED
def test_protected_route(client):
    email = unique_email("protected")

    client.post("/users", json={
        "name": "Protected",
        "email": email,
        "password": "123456"
    })

    login = client.post("/users/token", data={
        "username": email,
        "password": "123456"
    })

    token = login.json()["access_token"]

    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "authorized" in response.json()["message"]