from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# What the client sends when creating a user.
class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(max_length=254)


class UserCreate(UserBase):
    pass


# What the API sends back about a user.
class UserResponse(UserBase):
    # Lets FastAPI read the fields straight from the SQLAlchemy model.
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str


# What the client sends when creating a post.
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=9999)


class PostCreate(PostBase):
    # There is no login yet, so the client says who wrote the post.
    user_id: int


# What the API sends back about a post.
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse