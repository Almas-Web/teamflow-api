import pytest
import time

def unique_email(prefix):
    return f"{prefix}_{int(time.time() * 1000)}@gmail.com"

@pytest.mark.asyncio
async def test_register_user(client):
    email = unique_email("almas")
    
    response = await client.post("/users/", json={
        "name": "Almas",
        "email": email,
        "password": "1234"
    })
    assert response.status_code in [200, 201]
    assert response.json()["email"] == email

@pytest.mark.asyncio
async def test_login_user(client):
    email = unique_email("login")
    password = "123456"

    
    await client.post("/users/", json={"name": "Login Test", "email": email, "password": password})

    response = await client.post("/users/token", data={
        "username": email,
        "password": password
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_protected_route(client):
    email = unique_email("protected")
    password = "123456"

    await client.post("/users/", json={"name": "Protected", "email": email, "password": password})

    login = await client.post("/users/token", data={"username": email, "password": password})
    token = login.json()["access_token"]

    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "authorized" in response.json()["message"]