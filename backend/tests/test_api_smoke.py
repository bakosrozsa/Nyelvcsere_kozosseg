import os

os.environ.setdefault("NYELVCSERE_SECRET_KEY", "test-secret-key")

from fastapi.testclient import TestClient

from init_db import init_db
from main import app


client = TestClient(app)


def setup_module() -> None:
    # Ensure demo data exists for auth-related smoke checks.
    init_db()


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_users_endpoint_requires_authentication() -> None:
    response = client.get("/users")

    assert response.status_code == 401


def test_public_mentor_users_available_for_guests() -> None:
    response = client.get("/public/mentor-users")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload, "Expected at least one seeded mentor user"

    first = payload[0]
    assert {"id", "name", "email"}.issubset(first.keys())
    assert "hashed_password" not in first


def test_login_returns_bearer_token_for_seeded_mentor() -> None:
    response = client.post(
        "/login",
        data={"username": "anna.mentor@example.com", "password": "demo123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload.get("token_type") == "bearer"


def _login_token(username: str, password: str) -> str:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_student_cannot_access_pairing_suggestions() -> None:
    token = _login_token("peter.student@example.com", "demo123")
    response = client.get(
        "/pairing-suggestions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_student_users_endpoint_returns_self_only() -> None:
    token = _login_token("peter.student@example.com", "demo123")
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["email"] == "peter.student@example.com"


def test_student_cannot_create_group_session() -> None:
    token = _login_token("peter.student@example.com", "demo123")
    mentors_response = client.get("/mentor-profiles")
    assert mentors_response.status_code == 200
    mentor_profile_id = mentors_response.json()[0]["id"]

    response = client.post(
        "/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "mentor_profile_id": mentor_profile_id,
            "scheduled_time": "2030-01-01T10:00:00Z",
            "is_group": True,
            "max_students": 3,
        },
    )

    assert response.status_code == 403
