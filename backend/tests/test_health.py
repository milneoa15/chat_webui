"""Smoke tests for the FastAPI app."""

from fastapi.testclient import TestClient

from backend.app.main import create_app

client = TestClient(create_app())


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/health")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert "version" in payload
    assert "timestamp" in payload


def test_mock_models_fixture() -> None:
    response = client.get("/api/mock/models")
    payload = response.json()

    assert response.status_code == 200
    assert isinstance(payload, list)
    assert payload[0]["id"] == "tinyllama-q4"


def test_mock_chat_respects_model() -> None:
    response = client.post(
        "/api/mock/chat",
        json={
            "model_id": "tinyllama-q4",
            "prompt": "Hello?",
            "system_prompt": "test",
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["model_id"] == "tinyllama-q4"
    assert len(payload["stream"]) >= 1
