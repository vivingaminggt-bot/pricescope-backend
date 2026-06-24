from fastapi import APIRouter
from datetime import datetime

from scraper.simulator import PRODUCTS, get_platform_prices
from firebase.client import get_db

router = APIRouter()


@router.get("/")
def get_all_current_prices(save: bool = False):
    """
    Get current simulated prices across all platforms for all products.
    Pass ?save=true to also write a snapshot to Firestore.
    """
    output = []
    for product in PRODUCTS:
        prices = get_platform_prices(product)
        best = min(prices, key=lambda x: x["price"])
        output.append({
            "id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "platform_prices": prices,
            "best_price": best["price"],
            "best_platform": best["platform"],
        })

    if save:
        try:
            db = get_db()
            batch = db.batch()
            ts = datetime.utcnow().isoformat()
            for item in output:
                doc_ref = db.collection("price_snapshots").document(f"{item['id']}_{ts}")
                batch.set(doc_ref, {**item, "timestamp": ts})
            batch.commit()
        except Exception as e:
            return {"products": output, "saved": False, "save_error": str(e)}

    return {"products": output, "saved": save}


@router.get("/{product_id}")
def get_product_prices(product_id: str):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}

    prices = get_platform_prices(product)
    best = min(prices, key=lambda x: x["price"])
    return {
        "id": product["id"],
        "name": product["name"],
        "platform_prices": prices,
        "best_price": best["price"],
        "best_platform": best["platform"],
    }
