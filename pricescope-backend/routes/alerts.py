from fastapi import APIRouter
from scraper.simulator import PRODUCTS, generate_alert_for_product

router = APIRouter()


@router.get("/")
def get_all_alerts():
    """AI-style alerts: price drops, rises, and stability per product."""
    alerts = []
    for product in PRODUCTS:
        alert = generate_alert_for_product(product)
        alerts.append({
            "product_id": product["id"],
            "product_name": product["name"],
            **alert,
        })
    # Surface the most actionable alerts first
    priority = {"price_drop": 0, "rising": 1, "stable": 2}
    alerts.sort(key=lambda a: priority.get(a["type"], 3))
    return {"count": len(alerts), "alerts": alerts}
