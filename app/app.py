from typing import Annotated
from .schemas import PostCreate, PostResponse, UserResponse, UserCreate
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

DbDep = Annotated[Session, Depends(get_db)]


## route to render the home page with a list of posts
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: DbDep):

    result = db.execute(select(models.Post))
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "FastAPI Blog Home"},
    )


## route to get the details of a specific post by its ID
@app.get("/{post_id}", include_in_schema=False)
@app.get("/posts/{post_id}", name="post_details", include_in_schema=False)
def post_details(request: Request, post_id: int, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        title = post["title"][:50]
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

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
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


app.get("/api/users/{user_id}", response_model=UserResponse)


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
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


## route to return all posts as JSON
@app.get("/api/posts", response_model=list[PostResponse])
def return_posts(db: DbDep):
    result = db.execute(select(models.Post))
    return result.scalars().all()


@app.post(
    "/api/posts", response_model=UserResponse, status_code=status.HTTP_201_CREATED
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


## route to return a specific post by its ID as JSON
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def retun_post(post_id: int, db: DbDep):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().all()
    if post:
        return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found here :("
    )
