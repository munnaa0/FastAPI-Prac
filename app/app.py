from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
    friendly_date,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# These mounts expose uploaded media and frontend assets separately from API routes.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")
templates.env.filters["friendly_date"] = friendly_date

DbDep = Annotated[Session, Depends(get_db)]


# Keep both URLs available so templates can link to a readable collection path.
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: DbDep):

    result = db.execute(
        select(models.Post).order_by(
            models.Post.date_posted.desc(), models.Post.id.desc()
        )
    )
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "FastAPI Blog Home"},
    )


# The short route preserves the existing public URL; the prefixed route is clearer
# when generating links from templates.
@app.get("/{post_id}", include_in_schema=False)
@app.get("/posts/{post_id}", name="post_details", include_in_schema=False)
def post_details(request: Request, post_id: int, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request, "post.html", {"post": post, "title": title}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {"message": "Sorry The post isn't on our Servers"},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(request: Request, user_id: int, db: DbDep):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    result = db.execute(
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc(), models.Post.id.desc())
    )
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.post(
    "/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: DbDep):
    result = db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="UserName Already Exists"
        )

    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_user_email = result.scalars().first()
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Exmail Already Registered"
        )

    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DbDep):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")


@app.get("/api/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: DbDep):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )
    result = db.execute(
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc(), models.Post.id.desc())
    )
    posts = result.scalars().all()
    return posts


@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: DbDep):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(
            select(models.User).where(models.User.username == user_update.username),
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="UserName Already Exists",
            )

    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(
            select(models.User).where(models.User.email == user_update.email),
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exmail Already Registered",
            )

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbDep):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    db.delete(user)
    db.commit()


@app.get("/api/posts", response_model=list[PostResponse])
def return_posts(db: DbDep):
    result = db.execute(
        select(models.Post).order_by(
            models.Post.date_posted.desc(), models.Post.id.desc()
        )
    )
    return result.scalars().all()


@app.post(
    "/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED
)
def create_post(post: PostCreate, db: DbDep):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )
    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def retun_post(post_id: int, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found here :("
    )


@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(post_id: int, post_data: PostCreate, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found here :("
        )

    if post_data.user_id != post.user_id:
        result = db.execute(
            select(models.User).where(models.User.id == post_data.user_id),
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
            )

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post


@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(post_id: int, post_data: PostUpdate, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found here :("
        )

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found here :("
        )

    db.delete(post)
    db.commit()
