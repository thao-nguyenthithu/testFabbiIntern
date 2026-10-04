"""Todo tests."""

import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient, email: str = "todo@example.com") -> str:
    """Helper to register and get auth token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    """Test creating a new todo."""
    token = await get_auth_token(client, "create@example.com")

    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test Todo", "description": "A test todo item"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "A test todo item"
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_get_todos(client: AsyncClient):
    """Test getting todo list."""
    token = await get_auth_token(client, "list@example.com")

    # Create a todo first
    await client.post(
        "/api/v1/todos",
        json={"title": "List Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get todos
    response = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    """Test updating a todo."""
    token = await get_auth_token(client, "update@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Update Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Update it
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    """Test deleting a todo."""
    token = await get_auth_token(client, "delete@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Delete Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_single_todo(client: AsyncClient):
    """Test getting a single todo by ID."""
    token = await get_auth_token(client, "single@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Single Todo", "description": "Get me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Get it
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Todo"


@pytest.mark.asyncio
async def test_get_other_user_todo(client: AsyncClient):
    """Test that a user cannot get another user's todo."""
    token_a = await get_auth_token(client, "owner_get@example.com")
    token_b = await get_auth_token(client, "other_get@example.com")

    # User A creates a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "A's Todo"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    todo_id = create_response.json()["id"]

    # User B tries to get it
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_other_user_todo(client: AsyncClient):
    """Test that a user cannot update another user's todo."""
    token_a = await get_auth_token(client, "owner_update@example.com")
    token_b = await get_auth_token(client, "other_update@example.com")

    # User A creates a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "A's Todo"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    todo_id = create_response.json()["id"]

    # User B tries to update it
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404

    # User A still sees the original title
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.json()["title"] == "A's Todo"


@pytest.mark.asyncio
async def test_delete_other_user_todo(client: AsyncClient):
    """Test that a user cannot delete another user's todo."""
    token_a = await get_auth_token(client, "owner_delete@example.com")
    token_b = await get_auth_token(client, "other_delete@example.com")

    # User A creates a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "A's Todo"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    todo_id = create_response.json()["id"]

    # User B tries to delete it
    response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404

    # User A can still get it
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.status_code == 200
