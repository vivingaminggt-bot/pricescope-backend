from fastapi import APIRouter
from scraper.simulator import PRODUCTS, get_seasonal_analysis, evaluate_owner_price

router = APIRouter()


@router.get("/")
def get_all_seasonal_analysis():
    """
    Internal/owner-only endpoint: month-by-month best-price averages and a
    plain-language strategy note per product, based on the simulated year
    of price history. Not meant for the public shopper-facing UI.
    """
    results = []
    for product in PRODUCTS:
        analysis = get_seasonal_analysis(product)
        if analysis:
            results.append(analysis)
    return {"count": len(results), "analysis": results}


@router.get("/{product_id}")
def get_product_seasonal_analysis(product_id: str):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    return get_seasonal_analysis(product)


@router.get("/{product_id}/evaluate")
def evaluate_price(product_id: str, price: float):
    """
    Owner submits a proposed price (?price=1234.5) and gets back an AI
    verdict comparing it to that product's seasonal pricing pattern.
    """
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    result = evaluate_owner_price(product, price)
    if not result:
        return {"error": "Could not evaluate price"}
    return result
