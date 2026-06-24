from fastapi import APIRouter
from scraper.simulator import PRODUCTS

router = APIRouter()


@router.get("/")
def list_products():
    """Return all 10 tracked products with their base info."""
    return {"count": len(PRODUCTS), "products": PRODUCTS}


@router.get("/{product_id}")
def get_product(product_id: str):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}
