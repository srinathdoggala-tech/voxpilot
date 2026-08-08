"""Integration tests for VoxPilot FastAPI REST and WebSocket API endpoints."""

from fastapi.testclient import TestClient
from voxpilot.api.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "VoxPilot AI"


def test_knowledge_ingest_endpoint():
    response = client.post(
        "/api/v1/knowledge/ingest",
        json={"title": "Test Doc", "content": "This is test documentation content for RAG."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["chunks_created"] > 0


def test_evals_run_endpoint():
    response = client.post("/api/v1/evals/run")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scenarios"] > 0


def test_voice_websocket_endpoint():
    with client.websocket_connect("/api/v1/voice/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "session_started"

        # Send text turn
        websocket.send_json({"type": "text_turn", "text": "Hello VoxPilot"})
        resp = websocket.receive_json()
        assert resp["type"] == "turn_complete"
        assert resp["assistant_text"] != ""
