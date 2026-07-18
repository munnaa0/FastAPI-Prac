from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from typing import Any

app = FastAPI()

# Order of the endpoints matters, the first one will be checked first, so if you have a more specific endpoint, it should be defined before a more generic one.
@app.get("/shipment/latest")
def get_latest_shipment() -> dict[str, Any]:
    return {
        "shipment_id": 1235,
        "weight" : 120.65,
        "shipment_name": "First Shipment",
        "shipment_status": "In Transit",
    }

@app.get("/shipment/{id}")
def get_shipment(id: int) -> dict[str, Any]:
    return {
        "shipment_id": id,
        "weight" : 150.65,
        "shipment_name": "Random Shipment",
        "shipment_status": "Delivered",
    }


@app.get("/scalar", include_in_schema=False) 
def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar FastAPI")
