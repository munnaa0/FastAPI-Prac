from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from . import models
from .database import Base, DbDep, engine
from .routers import posts, users
from .utils import friendly_date

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# These mounts expose uploaded media and frontend assets separately from API routes.
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=PROJECT_DIR / "media"), name="media")

templates = Jinja2Templates(directory=APP_DIR / "templates")
templates.env.filters["friendly_date"] = friendly_date

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])


# Keep both URLs available so templates can link to a readable collection path.
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: DbDep):

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc(), models.Post.id.desc())
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
async def post_details(request: Request, post_id: int, db: DbDep):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
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
async def user_posts_page(request: Request, user_id: int, db: DbDep):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc(), models.Post.id.desc())
    )
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )
