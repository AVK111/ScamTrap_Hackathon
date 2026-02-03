import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_RESULT = {
    "status": "success",
    "sessionId": "s1",
    "reply": "ok",
    "classification": {},
    "scamDetected": False,
    "scamType": "Unknown",
    "riskScore": 10,
    "engagementMetrics": {
        "totalMessagesExchanged": 1,
        "engagementDurationSeconds": 0,
        "scammerMessages": 1,
        "userMessages": 0,
        "averageScammerMessageLength": 10,
        "conversationDepth": "shallow"
    },
    "extractedIntelligence": {},
    "agentNotes": "",
    "recommendations": [],
    "conversationStage": "early",
    "shouldContinue": True
}


def test_empty_body_returns_400():
    r = client.post("/handover", data="")
    assert r.status_code == 400


def test_invalid_json_returns_400():
    r = client.post("/handover", data="notjson", headers={"Content-Type": "application/json"})
    assert r.status_code == 400


def test_valid_json_returns_200(monkeypatch):
    monkeypatch.setattr("app.main.run_agents", lambda **kwargs: SAMPLE_RESULT)
    payload = {"sessionId": "s1", "message": {"text": "hello"}, "conversationHistory": []}
    r = client.post("/handover", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["sessionId"] == "s1"
