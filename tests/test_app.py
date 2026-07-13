import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app


client = TestClient(app)


def test_unregister_participant_removes_the_student_from_activity():
    response = client.delete("/activities/Chess%20Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    activities_response = client.get("/activities")
    activities = activities_response.json()["Chess Club"]
    assert "michael@mergington.edu" not in activities["participants"]


def test_unregister_participant_returns_404_for_unknown_participant():
    response = client.delete("/activities/Chess%20Club/participants/unknown@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
