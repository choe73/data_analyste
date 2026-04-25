"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
        "full_name": "Duplicate User",
    }
    # First registration
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpassword123",
            "full_name": "Login User",
        },
    )
    # Login using OAuth2 form
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "testpassword123",
            "full_name": "Wrong Pass User",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test accessing /me without authentication."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
