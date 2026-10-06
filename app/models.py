from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False,
    )

    # Optional, so it can be None when the user has no picture.
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    # Every post written by this user.
    # "back_populates" links both sides of the relationship together.
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
    )

    @property
    def image_path(self) -> str:
        """The URL the browser uses to show this user's picture."""
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # Width matches PostBase.title in schemas.py.
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # This must match a User.id.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # The user who wrote this post.
    author: Mapped[User] = relationship(
        back_populates="posts",
    )