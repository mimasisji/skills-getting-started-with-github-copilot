import sys
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_root_redirects_to_static_index():
    # Arrange
    request_path = "/"

    # Act
    response = client.get(request_path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog():
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    endpoint = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activity = client.get("/activities").json()["Chess Club"]
    assert email in activity["participants"]


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    endpoint = "/activities/Unknown%20Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_existing_participant_returns_400():
    # Arrange
    endpoint = "/activities/Chess%20Club/signup"
    email = "michael@mergington.edu"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_the_student_from_activity():
    # Arrange
    endpoint = "/activities/Chess%20Club/participants/michael@mergington.edu"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    activity = client.get("/activities").json()["Chess Club"]
    assert "michael@mergington.edu" not in activity["participants"]
