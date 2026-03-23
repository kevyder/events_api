import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

import src.database as database
from src.database import get_async_session
from src.main import app
from tests.conftest import (
    _override_get_async_session,
    _setup_test_db,
    _teardown_test_db,
    test_async_session_factory,
    test_engine,
)


def _future_iso(days: int = 1) -> str:
    """Return an ISO datetime string in the future."""
    return (datetime.now(UTC) + timedelta(days=days)).isoformat()


def _create_event_payload(**overrides) -> dict:
    """Build a valid event creation payload."""
    payload = {
        "name": "Test Event",
        "description": "A test event",
        "start_date": _future_iso(1),
        "end_date": _future_iso(2),
        "capacity": 100,
    }
    payload.update(overrides)
    return payload


def _create_session_payload(start_time: str, end_time: str, **overrides) -> dict:
    """Build a valid session creation payload."""
    payload = {
        "title": "Opening Keynote",
        "speaker": "Jane Doe",
        "start_time": start_time,
        "end_time": end_time,
    }
    payload.update(overrides)
    return payload


def _get_admin_token(client: TestClient) -> str:
    """Register an admin via seed and return the JWT token."""
    login_resp = client.post("/auth/login", json={"email": "admin@example.com", "password": "password123"})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def _get_user_token(client: TestClient) -> str:
    """Register a regular user and return the JWT token."""
    client.post("/auth/sign-up", json={"email": "user@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def _admin_client():
    """Context manager for a TestClient with a seeded admin user."""
    original_engine = database.engine
    original_session_factory = database.async_session_factory

    database.engine = test_engine
    database.async_session_factory = test_async_session_factory
    app.dependency_overrides[get_async_session] = _override_get_async_session

    _setup_test_db()

    with patch("src.auth.infrastructure.bootstrap.seed_admin.settings") as mock_settings:
        mock_settings.DEFAULT_ADMIN_EMAIL = "admin@example.com"
        mock_settings.DEFAULT_ADMIN_PASSWORD = "password123"

        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()
    database.engine = original_engine
    database.async_session_factory = original_session_factory

    _teardown_test_db()


# --- Public endpoints (no auth required) ---


def test_list_events_empty(client):
    """Test listing events returns an empty page when no events exist."""
    response = client.get("/events")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["pages"] == 0


def test_list_events_no_auth_required(client):
    """Test that listing events does not require authentication."""
    response = client.get("/events")
    assert response.status_code == 200


def test_get_event_not_found(client):
    """Test that fetching a non-existent event returns 404."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/events/{fake_id}")
    assert response.status_code == 404


def test_get_event_invalid_uuid(client):
    """Test that an invalid UUID returns 422."""
    response = client.get("/events/not-a-uuid")
    assert response.status_code == 422


def test_search_events_no_auth_required(client):
    """Test that searching events does not require authentication."""
    response = client.get("/events/search", params={"name": "test"})
    assert response.status_code == 200


def test_search_events_by_partial_name():
    """Test that searching events by partial name returns only matching events."""
    for c in _admin_client():
        token = _get_admin_token(c)

        c.post(
            "/events",
            json=_create_event_payload(name="Python Conference"),
            headers={"Authorization": f"Bearer {token}"},
        )
        c.post(
            "/events",
            json=_create_event_payload(name="FastAPI Workshop"),
            headers={"Authorization": f"Bearer {token}"},
        )
        c.post(
            "/events",
            json=_create_event_payload(name="PyData Meetup"),
            headers={"Authorization": f"Bearer {token}"},
        )

        response = c.get("/events/search", params={"name": "Python"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Python Conference"


def test_search_events_is_case_insensitive():
    """Test that searching events by name uses case-insensitive matching."""
    for c in _admin_client():
        token = _get_admin_token(c)

        c.post(
            "/events",
            json=_create_event_payload(name="React Summit"),
            headers={"Authorization": f"Bearer {token}"},
        )

        response = c.get("/events/search", params={"name": "react"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "React Summit"


def test_search_events_returns_empty_page_when_no_matches(client):
    """Test that searching with no matches returns an empty page."""
    response = client.get("/events/search", params={"name": "missing"})

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_search_events_requires_name_query_param(client):
    """Test that searching events requires the name query param."""
    response = client.get("/events/search")
    assert response.status_code == 422


# --- Admin-only endpoints: create ---


def test_create_event_requires_auth(client):
    """Test that creating an event without a token returns 401."""
    response = client.post("/events", json=_create_event_payload())
    assert response.status_code == 401


def test_create_event_requires_admin():
    """Test that a regular user cannot create events."""
    for c in _admin_client():
        token = _get_user_token(c)
        response = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


def test_create_event_success():
    """Test that an admin can create an event."""
    for c in _admin_client():
        token = _get_admin_token(c)
        payload = _create_event_payload()
        response = c.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["capacity"] == payload["capacity"]
        assert data["status"] == "upcoming"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data


def test_create_event_invalid_dates():
    """Test that invalid date order returns 422."""
    for c in _admin_client():
        token = _get_admin_token(c)
        payload = _create_event_payload(
            start_date=_future_iso(2),
            end_date=_future_iso(1),
        )
        response = c.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422


def test_create_event_zero_capacity():
    """Test that zero capacity returns 422."""
    for c in _admin_client():
        token = _get_admin_token(c)
        payload = _create_event_payload(capacity=0)
        response = c.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422


def test_create_event_negative_capacity():
    """Test that negative capacity returns 422."""
    for c in _admin_client():
        token = _get_admin_token(c)
        payload = _create_event_payload(capacity=-5)
        response = c.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422


# --- Public: list and get after creation ---


def test_list_and_get_event():
    """Test that created events appear in list and can be fetched by ID."""
    for c in _admin_client():
        token = _get_admin_token(c)
        payload = _create_event_payload(name="Visible Event")
        create_resp = c.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_resp.status_code == 201
        event_id = create_resp.json()["id"]

        # List (no auth) — paginated response
        list_resp = c.get("/events")
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] >= 1
        assert any(e["id"] == event_id for e in data["items"])
        assert "sessions" not in data["items"][0]

        # Get (no auth)
        get_resp = c.get(f"/events/{event_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "Visible Event"
        assert get_resp.json()["sessions"] == []


def test_get_event_includes_sorted_sessions():
    """Test that single event endpoint includes sessions sorted by start_time ascending."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(name="Visible Event"),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()
        event_id = event["id"]

        c.post(
            f"/events/{event_id}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=2)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=3)).isoformat(),
                title="Later Session",
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        c.post(
            f"/events/{event_id}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=1)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=2)).isoformat(),
                title="Earlier Session",
            ),
            headers={"Authorization": f"Bearer {token}"},
        )

        get_resp = c.get(f"/events/{event_id}")

        assert get_resp.status_code == 200
        sessions = get_resp.json()["sessions"]
        assert [session["title"] for session in sessions] == ["Earlier Session", "Later Session"]


def test_create_session_requires_admin():
    """Test that a regular user cannot create sessions."""
    for c in _admin_client():
        admin_token = _get_admin_token(c)
        user_token = _get_user_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        event = create_resp.json()

        response = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=1)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=2)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 403


def test_create_session_success():
    """Test that an admin can create a session within the event window."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()

        response = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=1)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=2)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Opening Keynote"
        assert data["speaker"] == "Jane Doe"
        assert data["event_id"] == event["id"]


def test_create_session_rejects_outside_event_window():
    """Test that a session outside the event bounds returns 422."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()

        response = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) - timedelta(minutes=30)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=1)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


def test_create_session_rejects_overlapping_schedule():
    """Test that overlapping sessions for the same event return 422."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()
        event_start = datetime.fromisoformat(event["start_date"])

        first_session_resp = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(event_start + timedelta(hours=1)).isoformat(),
                end_time=(event_start + timedelta(hours=2)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert first_session_resp.status_code == 201

        response = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(event_start + timedelta(hours=1, minutes=30)).isoformat(),
                end_time=(event_start + timedelta(hours=2, minutes=30)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


def test_update_session_success():
    """Test that an admin can update a session."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()
        session_resp = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=1)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=2)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        session_id = session_resp.json()["id"]

        response = c.patch(
            f"/events/{event['id']}/sessions/{session_id}",
            json={"title": "Updated Keynote"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Keynote"


def test_update_session_rejects_overlapping_schedule():
    """Test that updating a session into another session's timeslot returns 422."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()
        event_start = datetime.fromisoformat(event["start_date"])

        first_session_resp = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(event_start + timedelta(hours=1)).isoformat(),
                end_time=(event_start + timedelta(hours=2)).isoformat(),
                title="First Session",
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        second_session_resp = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(event_start + timedelta(hours=3)).isoformat(),
                end_time=(event_start + timedelta(hours=4)).isoformat(),
                title="Second Session",
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert first_session_resp.status_code == 201
        assert second_session_resp.status_code == 201

        response = c.patch(
            f"/events/{event['id']}/sessions/{second_session_resp.json()['id']}",
            json={
                "start_time": (event_start + timedelta(hours=1, minutes=30)).isoformat(),
                "end_time": (event_start + timedelta(hours=2, minutes=30)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


def test_delete_session_success():
    """Test that an admin can delete a session."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()
        session_resp = c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=1)).isoformat(),
                end_time=(datetime.fromisoformat(event["start_date"]) + timedelta(hours=2)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        session_id = session_resp.json()["id"]

        response = c.delete(
            f"/events/{event['id']}/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        get_resp = c.get(f"/events/{event['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["sessions"] == []


def test_update_event_rejects_dates_excluding_session():
    """Test that event date updates fail when existing sessions would fall outside the new range."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event = create_resp.json()
        event_start = datetime.fromisoformat(event["start_date"])

        c.post(
            f"/events/{event['id']}/sessions",
            json=_create_session_payload(
                start_time=(event_start + timedelta(hours=3)).isoformat(),
                end_time=(event_start + timedelta(hours=4)).isoformat(),
            ),
            headers={"Authorization": f"Bearer {token}"},
        )

        response = c.patch(
            f"/events/{event['id']}",
            json={"end_date": (event_start + timedelta(hours=2)).isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


# --- Admin-only endpoints: update (PATCH) ---


def test_patch_event_requires_auth(client):
    """Test that patching an event without a token returns 401."""
    fake_id = str(uuid.uuid4())
    response = client.patch(f"/events/{fake_id}", json={"name": "Updated"})
    assert response.status_code == 401


def test_patch_event_requires_admin():
    """Test that a regular user cannot update events."""
    for c in _admin_client():
        admin_token = _get_admin_token(c)
        user_token = _get_user_token(c)

        # Create event as admin
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        event_id = create_resp.json()["id"]

        # Try to update as regular user
        response = c.patch(
            f"/events/{event_id}",
            json={"name": "Hacked"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403


def test_patch_event_partial_update():
    """Test that PATCH only updates provided fields."""
    for c in _admin_client():
        token = _get_admin_token(c)
        payload = _create_event_payload(name="Original", description="Original desc")
        create_resp = c.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        event_id = create_resp.json()["id"]

        # Update only the name
        patch_resp = c.patch(
            f"/events/{event_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert patch_resp.status_code == 200
        data = patch_resp.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Original desc"  # preserved


def test_patch_event_not_found():
    """Test that patching a non-existent event returns 404."""
    for c in _admin_client():
        token = _get_admin_token(c)
        fake_id = str(uuid.uuid4())
        response = c.patch(
            f"/events/{fake_id}",
            json={"name": "Ghost"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


# --- Admin-only endpoints: delete ---


def test_delete_event_requires_auth(client):
    """Test that deleting an event without a token returns 401."""
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/events/{fake_id}")
    assert response.status_code == 401


def test_delete_event_requires_admin():
    """Test that a regular user cannot delete events."""
    for c in _admin_client():
        admin_token = _get_admin_token(c)
        user_token = _get_user_token(c)

        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        event_id = create_resp.json()["id"]

        response = c.delete(
            f"/events/{event_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403


def test_delete_event_success():
    """Test that an admin can delete an event."""
    for c in _admin_client():
        token = _get_admin_token(c)
        create_resp = c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )
        event_id = create_resp.json()["id"]

        delete_resp = c.delete(
            f"/events/{event_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_resp.status_code == 200

        # Verify it's gone
        get_resp = c.get(f"/events/{event_id}")
        assert get_resp.status_code == 404


def test_delete_event_not_found():
    """Test that deleting a non-existent event returns 404."""
    for c in _admin_client():
        token = _get_admin_token(c)
        fake_id = str(uuid.uuid4())
        response = c.delete(
            f"/events/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


# --- Pagination ---


def test_list_events_pagination():
    """Test that page and size query params control pagination."""
    for c in _admin_client():
        token = _get_admin_token(c)
        # Create 3 events
        for i in range(3):
            c.post(
                "/events",
                json=_create_event_payload(name=f"Event {i}"),
                headers={"Authorization": f"Bearer {token}"},
            )

        # Request page 1 with size 2
        resp = c.get("/events", params={"page": 1, "size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["pages"] == 2

        # Request page 2 with size 2
        resp = c.get("/events", params={"page": 2, "size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["page"] == 2


def test_list_events_sorted_by_created_at_desc():
    """Test that newer events appear first in the paginated list."""
    for c in _admin_client():
        token = _get_admin_token(c)

        first_resp = c.post(
            "/events",
            json=_create_event_payload(name="Older Event"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert first_resp.status_code == 201

        second_resp = c.post(
            "/events",
            json=_create_event_payload(name="Newer Event"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert second_resp.status_code == 201

        resp = c.get("/events", params={"page": 1, "size": 10})
        assert resp.status_code == 200

        items = resp.json()["items"]
        assert items[0]["name"] == "Newer Event"
        assert items[1]["name"] == "Older Event"


def test_list_events_page_beyond_results():
    """Test that requesting a page beyond available results returns empty items."""
    for c in _admin_client():
        token = _get_admin_token(c)
        c.post(
            "/events",
            json=_create_event_payload(),
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = c.get("/events", params={"page": 100, "size": 10})
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 1


def test_list_events_default_pagination(client):
    """Test that default pagination params are applied."""
    resp = client.get("/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["size"] == 50
