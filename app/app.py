from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


posts: list[dict] = [
    {
        "id": 4821,
        "author": "Alice",
        "title": "FastAPI Basics",
        "content": "An introduction to building APIs with FastAPI.",
        "date_posted": "2024-01-15",
    },
    {
        "id": 1197,
        "author": "Bob",
        "title": "Python Tips",
        "content": "Useful Python tricks for writing cleaner code.",
        "date_posted": "2024-01-20",
    },
    {
        "id": 5604,
        "author": "Charlie",
        "title": "Web Development",
        "content": "Exploring modern web development practices.",
        "date_posted": "2024-02-02",
    },
    {
        "id": 3088,
        "author": "Diana",
        "title": "Async Programming",
        "content": "How asynchronous code can improve performance.",
        "date_posted": "2024-02-10",
    },
    {
        "id": 7420,
        "author": "Ethan",
        "title": "Database Design",
        "content": "A quick guide to designing robust databases.",
        "date_posted": "2024-02-18",
    },
    {
        "id": 2156,
        "author": "Fiona",
        "title": "Testing APIs",
        "content": "Best practices for testing your FastAPI endpoints.",
        "date_posted": "2024-03-01",
    },
    {
        "id": 9031,
        "author": "George",
        "title": "Deployment",
        "content": "Tips for deploying Python applications smoothly.",
        "date_posted": "2024-03-12",
    },
    {
        "id": 6542,
        "author": "Hannah",
        "title": "Frontend Integration",
        "content": "Connecting backend services with modern frontend frameworks.",
        "date_posted": "2024-03-25",
    },
    {
        "id": 3875,
        "author": "Isaac",
        "title": "Security Essentials",
        "content": "Fundamental security practices every developer should know.",
        "date_posted": "2024-04-05",
    },
    {
        "id": 1430,
        "author": "Julia",
        "title": "Project Planning",
        "content": "How to plan and structure a successful software project.",
        "date_posted": "2024-04-15",
    },
]


## route to render the home page with a list of posts
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Hello"},
    )


## route to get the details of a specific post by its ID
@app.get("/{post_id}")
@app.get("/posts/{post_id}", name="post_details")
def post_details(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
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


## route to return all posts as JSON
@app.get("/posts")
@app.get("/api/posts")
def return_posts():
    return posts


## route to return a specific post by its ID as JSON
@app.get("/api/posts/{post_id}")
def retun_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found here :("
    )
