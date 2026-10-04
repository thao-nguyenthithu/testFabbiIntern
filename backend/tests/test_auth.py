"""Auth tests."""

import pytest
from httpx import AsyncClient
from datetime import timedelta
from unittest.mock import AsyncMock
from app.core.security import create_access_token, create_refresh_token, verify_token


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login after registration."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )

    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user info."""
    # Register and get token
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = reg_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout endpoint."""
    # Register and get token
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@example.com", "password": "password123"},
    )
    token = reg_response.json()["access_token"]

    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


@pytest.mark.asyncio
async def test_expired_token_rejected(client: AsyncClient):
    """Test that an expired access token is rejected."""
    # Register and get user id
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "expired@example.com", "password": "password123"},
    )
    user_id = verify_token(reg_response.json()["access_token"])["sub"]

    # Get current user with expired token
    token = create_access_token({"sub": user_id}, timedelta(minutes=-1))
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_rejected_as_access_token(client: AsyncClient):
    """Test that a refresh token cannot be used as an access token."""
    # Register and get refresh token
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongtype@example.com", "password": "password123"},
    )
    token = reg_response.json()["refresh_token"]

    # Get todos with refresh token
    response = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_refresh_token_rejected(client: AsyncClient):
    """Test that an expired refresh token is rejected."""
    # Register and get user id
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "expiredrefresh@example.com", "password": "password123"},
    )
    user_id = verify_token(reg_response.json()["access_token"])["sub"]

    # Refresh with expired token
    token = create_refresh_token({"sub": user_id}, timedelta(days=-1))
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_failed(client: AsyncClient):
    """Test login with an unknown email."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, monkeypatch):
    """Test that the database blocks a duplicate email."""
    # Skip the email check, like two requests arriving at the same time
    monkeypatch.setattr(
        "app.api.v1.auth.get_user_by_email", AsyncMock(return_value=None)
    )
    user = {"email": "dup@example.com", "password": "password123"}

    await client.post("/api/v1/auth/register", json=user)
    response = await client.post("/api/v1/auth/register", json=user)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_missing_token_returns_401(client: AsyncClient):
    """Test that a request without a token gets 401, not 403."""
    response = await client.get("/api/v1/todos")
    assert response.status_code == 401
