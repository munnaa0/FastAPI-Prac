from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from typing import Any

app = FastAPI()

shipments: dict[int, dict[str, Any]] = {
    125: {
        "weight" : 120.65,
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
    }
}

@app.get("/")
def home() -> dict[str, Any]:
    return {"message": "Welcome to the Shipment API Homepage!"}

# Order of the endpoints matters, the first one will be checked first, so if you have a more specific endpoint, it should be defined before a more generic one.
@app.get("/shipment/latest")
def get_latest_shipment() -> dict[str, Any]:
    id: int = max(shipments.keys())
    return shipments[id]

@app.get("/shipment/{id}")
def get_shipment(id: int) -> dict[str, Any]:
    if id not in shipments:
        return {"error": "Shipment not found"}
    else:
        return shipments[id]


@app.get("/scalar", include_in_schema=False) 
def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar FastAPI")
