from unittest.mock import patch

from fastapi.testclient import TestClient

import src.database as database
from src.database import get_async_session
from src.main import app
from tests.conftest import _override_get_async_session, test_async_session_factory, test_engine


def test_register_and_login(client):
    """Test registering a user and then logging in."""
    # Register
    response = client.post("/auth/sign-up", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data

    # Login
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    """Test that registering with the same email returns 409."""
    client.post("/auth/sign-up", json={"email": "dup@example.com", "password": "password123"})
    response = client.post("/auth/sign-up", json={"email": "dup@example.com", "password": "password123"})
    assert response.status_code == 409


def test_register_invalid_email(client):
    """Test that an invalid email returns 422."""
    response = client.post("/auth/sign-up", json={"email": "not-an-email", "password": "password123"})
    assert response.status_code == 422


def test_register_short_password(client):
    """Test that password must be at least 8 characters."""
    response = client.post("/auth/sign-up", json={"email": "short@example.com", "password": "short"})
    assert response.status_code == 422


def test_login_wrong_password(client):
    """Test that wrong password returns 401."""
    client.post("/auth/sign-up", json={"email": "login@example.com", "password": "password123"})
    response = client.post("/auth/login", json={"email": "login@example.com", "password": "wrong"})
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test that login with unknown email returns 401."""
    response = client.post("/auth/login", json={"email": "nobody@example.com", "password": "password123"})
    assert response.status_code == 401


def test_get_me(client):
    """Test /auth/me returns current user info."""
    client.post("/auth/sign-up", json={"email": "me@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "me@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["role"] == "user"


def test_get_me_no_token(client):
    """Test /auth/me without token returns 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    """Test /auth/me with invalid token returns 401."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401


def test_admin_only_with_seeded_admin():
    """Test admin-only endpoint with an admin user created by seed_admin during lifespan."""
    original_engine = database.engine
    original_session_factory = database.async_session_factory

    database.engine = test_engine
    database.async_session_factory = test_async_session_factory
    app.dependency_overrides[get_async_session] = _override_get_async_session

    with patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings:
        mock_settings.DEFAULT_ADMIN_EMAIL = "admin@example.com"
        mock_settings.DEFAULT_ADMIN_PASSWORD = "password123"

        with TestClient(app) as c:
            login_resp = c.post("/auth/login", json={"email": "admin@example.com", "password": "password123"})
            assert login_resp.status_code == 200
            token = login_resp.json()["access_token"]

            response = c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
            assert response.json()["email"] == "admin@example.com"

    app.dependency_overrides.clear()
    database.engine = original_engine
    database.async_session_factory = original_session_factory


def test_register_admin_requires_admin(client):
    """Test that /auth/sign-up-admin requires an admin user."""
    # Register a regular user
    client.post("/auth/sign-up", json={"email": "regular@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "regular@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]

    # Try to register an admin — should be forbidden
    response = client.post(
        "/auth/sign-up-admin",
        json={"email": "newadmin@example.com", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_register_admin_with_seeded_admin():
    """Test that a seeded admin can create new admin users via /auth/sign-up-admin."""
    original_engine = database.engine
    original_session_factory = database.async_session_factory

    database.engine = test_engine
    database.async_session_factory = test_async_session_factory
    app.dependency_overrides[get_async_session] = _override_get_async_session

    with patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings:
        mock_settings.DEFAULT_ADMIN_EMAIL = "admin@example.com"
        mock_settings.DEFAULT_ADMIN_PASSWORD = "password123"

        with TestClient(app) as c:
            # Login as the seeded admin
            login_resp = c.post("/auth/login", json={"email": "admin@example.com", "password": "password123"})
            assert login_resp.status_code == 200
            token = login_resp.json()["access_token"]

            # Create a new admin
            response = c.post(
                "/auth/sign-up-admin",
                json={"email": "newadmin@example.com", "password": "password123"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "newadmin@example.com"
            assert data["role"] == "admin"

    app.dependency_overrides.clear()
    database.engine = original_engine
    database.async_session_factory = original_session_factory
