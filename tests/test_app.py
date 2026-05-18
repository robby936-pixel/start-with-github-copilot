from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_INITIAL_ACTIVITIES = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(_INITIAL_ACTIVITIES))


def setup_function():
    reset_activities()


def teardown_function():
    reset_activities()


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_post_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_post_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already registered for this activity"


def test_post_signup_invalid_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "user@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_success():
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_delete_participant_not_found_returns_404():
    activity_name = "Chess Club"
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": "missing@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"


def test_delete_participant_invalid_activity_returns_404():
    response = client.delete(
        "/activities/NoActivity/participants", params={"email": "user@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
