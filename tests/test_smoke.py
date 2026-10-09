"""Smoke tests. These never touch blog.db - see assert below."""

import os
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="blog-tests-")
# Must be set before importing app.database, since the engine is built at import.
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"

import pytest
from fastapi.testclient import TestClient

from app.app import app
from app.database import SQLALCHEMY_DATABASE_URL, Base, engine


def test_never_uses_the_real_database():
    assert "blog.db" not in SQLALCHEMY_DATABASE_URL
    assert "blog.db" not in str(engine.url)


@pytest.fixture(scope="module", autouse=True)
def _tables():
    # A fresh temp file, so create_all is enough and no drop is ever needed.
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def user(client):
    r = client.post("/api/users", json={"username": "alex", "email": "a@b.com"})
    assert r.status_code == 201, r.text
    return r.json()


def test_create_user_returns_default_image(client, user):
    assert user["image_file"] is None
    assert user["image_path"] == "/media/profile_pics/default.jpg"


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "alex", "email": "other@b.com"},  # username taken
        {"username": "other", "email": "a@b.com"},  # email taken
    ],
)
def test_duplicate_user_rejected(client, user, payload):
    assert client.post("/api/users", json=payload).status_code == 400


def test_create_and_read_post(client, user):
    r = client.post(
        "/api/posts", json={"user_id": user["id"], "title": "T", "content": "C"}
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["author"]["username"] == "alex"

    assert client.get(f"/api/posts/{body['id']}").json()["title"] == "T"
    assert client.get("/api/posts/999999").status_code == 404
    assert client.get("/api/users/999999").status_code == 404


def test_create_post_requires_existing_user(client):
    r = client.post("/api/posts", json={"user_id": 999999, "title": "T", "content": "C"})
    assert r.status_code == 404


@pytest.mark.parametrize("path", ["/", "/posts", "/{id}", "/posts/{id}", "/users/{id}/posts"])
def test_html_pages_render(client, user, path):
    post_id = client.get("/api/posts").json()[0]["id"]
    r = client.get(path.format(id=post_id))
    assert r.status_code == 200
    assert "alex" in r.text
    assert "<app.models.User object" not in r.text


def test_missing_post_page_404s(client):
    assert client.get("/posts/999999").status_code == 404


def test_posts_are_newest_first(client, user):
    ids = []
    for title in ("first", "second", "third"):
        r = client.post(
            "/api/posts", json={"user_id": user["id"], "title": title, "content": "c"}
        )
        ids.append(r.json()["id"])

    titles = [p["title"] for p in client.get("/api/posts").json()]
    assert titles[: len(ids)] == ["third", "second", "first"], titles


def test_dates_are_human_readable(client, user):
    r = client.post(
        "/api/posts", json={"user_id": user["id"], "title": "T", "content": "C"}
    )
    stamp = r.json()["date_posted"]
    assert "T" not in stamp, stamp

    post_id = r.json()["id"]
    assert stamp in client.get(f"/posts/{post_id}").text
