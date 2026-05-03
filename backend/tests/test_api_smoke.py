import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

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


def test_student_users_endpoint_excludes_self_and_mentors() -> None:
    token = _login_token("peter.student@example.com", "demo123")
    peer_email = f"peer.student.{uuid4().hex}@example.com"

    register_response = client.post(
        "/register",
        json={
            "name": "Test Student Peer",
            "email": peer_email,
            "password": "demo123",
            "role": "student",
        },
    )
    assert register_response.status_code == 201

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    emails = {user["email"] for user in payload}
    assert peer_email in emails
    assert "peter.student@example.com" not in emails
    assert "anna.mentor@example.com" not in emails


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


def test_mentor_evaluation_requires_explicit_update_flag() -> None:
    mentor_token = _login_token("anna.mentor@example.com", "demo123")
    student_token = _login_token("peter.student@example.com", "demo123")

    mentor_profiles_response = client.get("/mentor-profiles")
    assert mentor_profiles_response.status_code == 200
    mentor_profiles_payload = mentor_profiles_response.json()
    assert mentor_profiles_payload
    mentor_profile_id = mentor_profiles_payload[0]["id"]

    create_response = client.post(
        "/sessions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "mentor_profile_id": mentor_profile_id,
            "scheduled_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "is_group": False,
            "max_students": None,
        },
    )
    assert create_response.status_code == 201
    created_session = create_response.json()
    session_id = created_session["id"]

    complete_response = client.put(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"status": "completed"},
    )
    assert complete_response.status_code == 200

    participants_response = client.get(
        f"/sessions/{session_id}/participants",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert participants_response.status_code == 200
    participants_payload = participants_response.json()
    assert participants_payload, "Expected at least one participant in completed session"
    student_id = participants_payload[0]["student_id"]

    first_save = client.put(
        f"/sessions/{session_id}/evaluations/{student_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"rating": 4, "notes": "Első értékelés"},
    )
    assert first_save.status_code == 200

    blocked_update = client.put(
        f"/sessions/{session_id}/evaluations/{student_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"rating": 5, "notes": "Második értékelés"},
    )
    assert blocked_update.status_code == 400
    assert "allow_update" in blocked_update.json().get("detail", "")

    allowed_update = client.put(
        f"/sessions/{session_id}/evaluations/{student_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"rating": 5, "notes": "Frissített értékelés", "allow_update": True},
    )
    assert allowed_update.status_code == 200
    assert allowed_update.json()["rating"] == 5


def test_progress_log_requires_explicit_update_flag() -> None:
    mentor_token = _login_token("anna.mentor@example.com", "demo123")
    student_token = _login_token("peter.student@example.com", "demo123")

    mentor_profiles_response = client.get("/mentor-profiles")
    assert mentor_profiles_response.status_code == 200
    mentor_profiles_payload = mentor_profiles_response.json()
    assert mentor_profiles_payload
    mentor_profile_id = mentor_profiles_payload[0]["id"]

    create_response = client.post(
        "/sessions",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "mentor_profile_id": mentor_profile_id,
            "scheduled_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "is_group": False,
            "max_students": None,
        },
    )
    assert create_response.status_code == 201
    created_session = create_response.json()
    session_id = created_session["id"]

    complete_response = client.put(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"status": "completed"},
    )
    assert complete_response.status_code == 200

    first_save = client.put(
        f"/sessions/{session_id}/progress-log",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"rating": 4, "notes": "Első megjeegyzés"},
    )
    assert first_save.status_code == 200

    blocked_update = client.put(
        f"/sessions/{session_id}/progress-log",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"rating": 5, "notes": "Második megjegyzés"},
    )
    assert blocked_update.status_code == 400
    assert "allow_update" in blocked_update.json().get("detail", "")

    allowed_update = client.put(
        f"/sessions/{session_id}/progress-log",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"rating": 5, "notes": "Frissített megjegyzés", "allow_update": True},
    )
    assert allowed_update.status_code == 200
    assert allowed_update.json()["rating"] == 5
