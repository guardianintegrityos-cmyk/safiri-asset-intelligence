# test_auth_endpoints.py

import pytest
from httpx import AsyncClient
from main import app  # Make sure this points to your FastAPI app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "username": "testuser",
            "password": "testpassword"
        })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"

@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Make sure the user exists first
        await ac.post("/auth/register", json={
            "username": "loginuser",
            "password": "loginpassword"
        })
        response = await ac.post("/auth/login", data={
            "username": "loginuser",
            "password": "loginpassword"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"