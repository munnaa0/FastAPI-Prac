from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from . import models
from .database import Base, engine, get_db
from .schemas import PostCreate, PostResponse, UserCreate, UserResponse

# The folder that holds app/, templates/, static/ and media/.
# Using a full path means the app still starts if you run it
# from a different folder.
BASE_DIR = Path(__file__).resolve().parent.parent


# This runs once when the app starts and once when it stops.
# "create_all" makes the tables if they do not exist yet.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

# These two lines let the browser load CSS, images and uploads.
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

# Loads .html files from the templates folder.
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ---------------------------------------------------------------------------
# route to show every post
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Session = Depends(get_db)):
    # Read all posts. "selectinload" grabs the author in one extra
    # query instead of one query per post.
    query = select(models.Post)
    query = query.options(selectinload(models.Post.author))

    result = db.execute(query)
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "FastAPI Blog Home"},
    )


# ---------------------------------------------------------------------------
# route to show one post
# ---------------------------------------------------------------------------
# The two decorators below let one function answer two URLs:
# /posts/1 and /1. The second one needs the ID as text, because it also
# matches /anything, so we check that it is a number by hand.
@app.get("/posts/{post_id}", name="post_details", include_in_schema=False)
@app.get("/{post_id}", include_in_schema=False)
def post_details(request: Request, post_id: str, db: Session = Depends(get_db)):
    if post_id.isdigit():
        post = db.get(
            models.Post,
            int(post_id),
            options=[selectinload(models.Post.author)],
        )
    else:
        post = None

    if post is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Sorry The post isn't on our Servers"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # The <title> tag shows at most 50 characters of the post title.
    return templates.TemplateResponse(
        request,
        "post.html",
        {"post": post, "title": post.title[:50]},
    )


# ---------------------------------------------------------------------------
# route to show the posts of one user
# ---------------------------------------------------------------------------
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    query = select(models.Post)
    query = query.where(models.Post.user_id == user_id)
    query = query.options(selectinload(models.Post.author))

    result = db.execute(query)
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
        },
    )


# ---------------------------------------------------------------------------
# API: create a user
# ---------------------------------------------------------------------------
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Usernames must be unique.
    query = select(models.User)
    query = query.where(models.User.username == user.username)

    result = db.execute(query)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username Already Exists",
        )

    # Emails must be unique too.
    query = select(models.User)
    query = query.where(models.User.email == user.email)

    result = db.execute(query)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Already Exists",
        )

    # Build the row and put it in the database.
    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)

    try:
        db.commit()
    except SQLAlchemyError:
        # Undo the failed work so the next query still works.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could Not Save User",
        ) from None

    # After a commit the object has no id yet, so read it back.
    db.refresh(new_user)

    return new_user


# ---------------------------------------------------------------------------
# API: get one user
# ---------------------------------------------------------------------------
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    return user


# ---------------------------------------------------------------------------
# API: get the posts of one user
# ---------------------------------------------------------------------------
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    query = select(models.Post)
    query = query.where(models.Post.user_id == user_id)
    query = query.options(selectinload(models.Post.author))

    result = db.execute(query)

    return result.scalars().all()


# ---------------------------------------------------------------------------
# API: return all posts as JSON
# ---------------------------------------------------------------------------
@app.get("/api/posts", response_model=list[PostResponse])
def return_posts(db: Session = Depends(get_db)):
    query = select(models.Post)
    query = query.options(selectinload(models.Post.author))

    result = db.execute(query)

    return result.scalars().all()


# ---------------------------------------------------------------------------
# API: create a post
# ---------------------------------------------------------------------------
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # A post needs a real user, so check that the id exists first.
    user = db.get(models.User, post.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could Not Save Post",
        ) from None

    db.refresh(new_post)

    return new_post


# ---------------------------------------------------------------------------
# API: return one post as JSON
# ---------------------------------------------------------------------------
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def return_post(post_id: int, db: Session = Depends(get_db)):
    # "selectinload" is needed because the JSON includes the author.
    post = db.get(
        models.Post,
        post_id,
        options=[selectinload(models.Post.author)],
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post Not Found here :(",
        )

    return post