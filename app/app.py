from typing import Any  # noqa: I001
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

shipments: dict[int, dict[str, Any]] = {
    125: {
        "weight": 120.65,
        "shipment_name": "First Shipment",
        "shipment_status": "In Transit",
    },
    126: {
        "weight": 45.0,
        "shipment_name": "Books Order",
        "shipment_status": "Delivered",
    },
    127: {
        "weight": 78.25,
        "shipment_name": "Electronics Batch",
        "shipment_status": "Pending",
    },
    128: {
        "weight": 5.5,
        "shipment_name": "Sample Packet",
        "shipment_status": "In Transit",
    },
    129: {
        "weight": 250.0,
        "shipment_name": "Furniture Crate",
        "shipment_status": "Delivered",
    },
    130: {
        "weight": 12.75,
        "shipment_name": "Clothing Box",
        "shipment_status": "In Transit",
    },
    131: {
        "weight": 300.4,
        "shipment_name": "Industrial Parts",
        "shipment_status": "Pending",
    },
    132: {
        "weight": 0.95,
        "shipment_name": "Accessory",
        "shipment_status": "Delivered",
    },
    133: {
        "weight": 67.3,
        "shipment_name": "Kitchenware",
        "shipment_status": "In Transit",
    },
    134: {
        "weight": 19.9,
        "shipment_name": "Cosmetics",
        "shipment_status": "Delivered",
    },
    135: {
        "weight": 142.0,
        "shipment_name": "Outdoor Gear",
        "shipment_status": "Pending",
    },
}


# Order of the endpoints matters, the first one will be checked first, so if you have a more specific endpoint, it should be defined before a more generic one.
@app.get("/shipment/latest", include_in_schema=False)
def get_latest_shipment() -> dict[str, Any]:
    id: int = max(shipments.keys())
    return shipments[id]


@app.get("/shipment/{id}", include_in_schema=False)
def get_shipment(id: int) -> dict[str, Any]:
    if id not in shipments:
        return {"error": "Shipment not found"}
    else:
        return shipments[id]


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar FastAPI")


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


@app.get("/")
@app.get("/posts", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Hello"},
    )


@app.get("/api/posts")
def return_posts():
    return posts
