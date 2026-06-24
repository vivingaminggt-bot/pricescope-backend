from fastapi import APIRouter
from scraper.simulator import PRODUCTS, get_year_history

router = APIRouter()


@router.get("/{product_id}")
def get_product_history(product_id: str):
    """Return ~52 weekly price points per platform over the last year."""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}

    history = get_year_history(product)
    return {"id": product["id"], "name": product["name"], "history": history}


@router.get("/")
def get_all_history():
    """Return 1-year history for all 10 products (larger payload)."""
    result = []
    for product in PRODUCTS:
        result.append({
            "id": product["id"],
            "name": product["name"],
            "history": get_year_history(product),
        })
    return {"products": result}
