"""The test suite must never touch the development database."""

from app.database import SQLALCHEMY_DATABASE_URL, engine


def test_never_uses_the_real_database():
    assert "blog.db" not in SQLALCHEMY_DATABASE_URL
    assert "blog.db" not in str(engine.url)
