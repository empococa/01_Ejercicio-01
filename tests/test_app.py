import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(copy.deepcopy(original))


def test_get_activities_contains_chess_club():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_post_signup_adds_participant_and_prevents_duplicate():
    email = "newstudent@example.edu"
    activity = "Chess Club"
    path = urllib.parse.quote(activity, safe="")

    resp = client.post(f"/activities/{path}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    resp_dup = client.post(f"/activities/{path}/signup", params={"email": email})
    assert resp_dup.status_code == 400


def test_delete_participant_and_nonexistent_returns_404():
    email = "toremove@example.edu"
    activity = "Chess Club"
    path = urllib.parse.quote(activity, safe="")

    resp_add = client.post(f"/activities/{path}/signup", params={"email": email})
    assert resp_add.status_code == 200
    assert email in activities[activity]["participants"]

    resp_del = client.delete(f"/activities/{path}/participants", params={"email": email})
    assert resp_del.status_code == 200
    assert email not in activities[activity]["participants"]

    resp_del2 = client.delete(f"/activities/{path}/participants", params={"email": email})
    assert resp_del2.status_code == 404
