from datetime import UTC, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer


def friendly_date(value: datetime | None) -> str:
    # SQLite drops the timezone, so naive values are UTC.
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone().strftime("%b %d, %Y at %I:%M %p")


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(max_length=50)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    # Lets Pydantic build this schema directly from a database model's attributes.
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=9999)


class PostCreate(PostBase):
    user_id: int  # TEMPORARY


class PostResponse(PostBase):
    # Lets Pydantic build this schema directly from a database model's attributes.
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse

    @field_serializer("date_posted")
    def serialize_date_posted(self, value: datetime) -> str:
        return friendly_date(value)
