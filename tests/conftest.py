"""Shared test fixtures.

The temp database must be configured before the app is imported, since the
engine is built at import time.
"""

import os
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="blog-tests-")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP_DIR}/test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    # Lifespan creates the tables in the temp file, so no fixture is needed.
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def user(client):
    r = client.post(
        "/api/users",
        json={"username": "alex", "email": "a@b.com", "password": "correct-horse"},
    )
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture(scope="session")
def post(client, user):
    r = client.post(
        "/api/posts", json={"user_id": user["id"], "title": "T", "content": "C"}
    )
    assert r.status_code == 201, r.text
    return r.json()
