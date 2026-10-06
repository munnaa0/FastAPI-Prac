import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app, get_db
from app.database import Base
from app.models import Post, User

@pytest.fixture
def engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def client(engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # ponytail: distinct authors per post on purpose. If every post shares one
    # author the session identity map dedupes the lazy load and the N+1 test
    # passes even when eager loading is removed.
    with TestingSession() as db:
        for i in range(5):
            db.add(User(username=f"user{i}", email=f"user{i}@example.com"))
        db.commit()
        users = db.query(User).order_by(User.id).all()
        for i, user in enumerate(users):
            db.add(
                Post(
                    title="Hello World" if i == 0 else f"Post {i}",
                    content="First post body",
                    user_id=user.id,
                )
            )
        db.commit()

    def override_get_db():
        with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Hello World" in r.text
    assert "user0" in r.text
    assert "app.models.User object" not in r.text


def test_post_detail_page(client):
    assert client.get("/posts/1").status_code == 200
    assert client.get("/1").status_code == 200


def test_post_detail_404(client):
    assert client.get("/posts/999").status_code == 404
    assert client.get("/999").status_code == 404


def test_catch_all_is_404_not_422(client):
    r = client.get("/definitely-not-a-post")
    assert r.status_code == 404


def test_user_posts_page(client):
    r = client.get("/users/1/posts")
    assert r.status_code == 200
    assert "Hello World" in r.text


def test_user_posts_page_404(client):
    assert client.get("/users/999/posts").status_code == 404


def test_api_get_posts(client):
    r = client.get("/api/posts")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 5
    assert body[0]["title"] == "Hello World"
    assert body[0]["author"]["username"] == "user0"


def test_api_get_post_by_id(client):
    r = client.get("/api/posts/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_api_get_post_404(client):
    assert client.get("/api/posts/999").status_code == 404


def test_api_get_user(client):
    r = client.get("/api/users/1")
    assert r.status_code == 200
    assert r.json()["username"] == "user0"


def test_api_get_user_404(client):
    assert client.get("/api/users/999").status_code == 404


def test_api_user_posts(client):
    r = client.get("/api/users/1/posts")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_api_create_user(client):
    r = client.post("/api/users", json={"username": "bob", "email": "bob@example.com"})
    assert r.status_code == 201
    assert r.json()["username"] == "bob"


def test_api_create_user_duplicate_username(client):
    r = client.post(
        "/api/users", json={"username": "user0", "email": "new@example.com"}
    )
    assert r.status_code == 400


def test_api_create_user_duplicate_email(client):
    r = client.post(
        "/api/users", json={"username": "carl", "email": "user0@example.com"}
    )
    assert r.status_code == 400


def test_api_create_user_invalid_email(client):
    r = client.post("/api/users", json={"username": "dave", "email": "not-an-email"})
    assert r.status_code == 422


def test_api_create_post(client):
    r = client.post("/api/posts", json={"user_id": 1, "title": "Second", "content": "Body"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Second"
    assert body["author"]["username"] == "user0"


def test_api_create_post_unknown_user(client):
    r = client.post("/api/posts", json={"user_id": 999, "title": "T", "content": "C"})
    assert r.status_code == 404


def test_api_create_post_title_over_max_length(client):
    r = client.post(
        "/api/posts", json={"user_id": 1, "title": "x" * 501, "content": "C"}
    )
    assert r.status_code == 422


def test_openapi_schema_builds(client):
    assert client.get("/openapi.json").status_code == 200


def test_n_plus_one_posts_page_queries(client, engine):
    """Posts list must eager-load authors: query count must not scale with rows."""
    from sqlalchemy import event

    count = {"n": 0}

    @event.listens_for(engine, "before_cursor_execute")
    def _count(conn, cursor, statement, params, context, executemany):
        count["n"] += 1

    try:
        r = client.get("/api/posts")
        assert r.status_code == 200
        assert len(r.json()) == 5
        # 5 posts by 5 distinct authors: eager loading keeps this at 2 queries
        assert count["n"] <= 3, f"N+1: {count['n']} queries for the posts list"
    finally:
        event.remove(engine, "before_cursor_execute", _count)