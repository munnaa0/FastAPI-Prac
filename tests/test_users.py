"""User creation, lookup, update and deletion."""

import pytest


def test_create_user_returns_default_image(user):
    assert user["image_file"] is None
    assert user["image_path"] == "/media/profile_pics/default.jpg"


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "alex", "email": "other@b.com", "password": "correct-horse"},
        {"username": "other", "email": "a@b.com", "password": "correct-horse"},
    ],
)
def test_duplicate_user_rejected(client, user, payload):
    assert client.post("/api/users", json=payload).status_code == 400


def test_get_user(client, user):
    r = client.get(f"/api/users/{user['id']}")
    assert r.status_code == 200
    assert r.json()["username"] == "alex"


def test_get_missing_user_404s(client):
    assert client.get("/api/users/999999").status_code == 404


def test_update_user(client, user):
    r = client.patch(f"/api/users/{user['id']}", json={"username": "alex2"})
    assert r.status_code == 200
    assert r.json()["username"] == "alex2"

    # put it back, the session fixture is shared
    assert (
        client.patch(f"/api/users/{user['id']}", json={"username": "alex"}).status_code
        == 200
    )


def test_delete_user(client):
    r = client.post(
        "/api/users",
        json={"username": "temp", "email": "temp@b.com", "password": "correct-horse"},
    )
    user_id = r.json()["id"]
    assert client.delete(f"/api/users/{user_id}").status_code == 204
    assert client.get(f"/api/users/{user_id}").status_code == 404
