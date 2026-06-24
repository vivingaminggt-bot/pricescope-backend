import random
import hashlib
from datetime import datetime, timedelta

PLATFORMS = ["Amazon", "Flipkart", "Meesho", "Croma", "JioMart"]

PRODUCTS = [
    {"id": "p1", "name": "Wireless Noise-Cancelling Headphones", "category": "Audio", "base_price": 8999},
    {"id": "p2", "name": "Smartwatch Pro Series 5", "category": "Wearables", "base_price": 12999},
    {"id": "p3", "name": "4K Ultra HD Smart TV 55-inch", "category": "Electronics", "base_price": 45999},
    {"id": "p4", "name": "Gaming Laptop RTX Series", "category": "Electronics", "base_price": 89999},
    {"id": "p5", "name": "Robot Vacuum Cleaner", "category": "Appliances", "base_price": 15999},
    {"id": "p6", "name": "Wireless Gaming Mouse", "category": "Gaming", "base_price": 2499},
    {"id": "p7", "name": "Mechanical Gaming Keyboard RGB", "category": "Gaming", "base_price": 4999},
    {"id": "p8", "name": "Air Fryer Digital 5L", "category": "Appliances", "base_price": 6499},
    {"id": "p9", "name": "Fitness Tracker Band", "category": "Wearables", "base_price": 1999},
    {"id": "p10", "name": "Bluetooth Portable Speaker", "category": "Audio", "base_price": 3499},
]


def _seeded_random(seed_str: str) -> random.Random:
    """Deterministic RNG per product+platform so prices are stable between calls."""
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)


def get_platform_prices(product: dict, on_date: datetime = None):
    """Generate a realistic price per platform for a product on a given date."""
    if on_date is None:
        on_date = datetime.utcnow()

    results = []
    for platform in PLATFORMS:
        rng = _seeded_random(f"{product['id']}-{platform}-{on_date.strftime('%Y-%m-%d')}")
        # Each platform has a slightly different markup/discount tendency
        platform_bias = {
            "Amazon": -0.03, "Flipkart": -0.05, "Meesho": -0.10,
            "Croma": 0.02, "JioMart": -0.01,
        }[platform]
        daily_fluctuation = rng.uniform(-0.04, 0.04)
        price = product["base_price"] * (1 + platform_bias + daily_fluctuation)
        price = round(price / 10) * 10  # round to nearest 10
        results.append({"platform": platform, "price": float(price)})

    return results


def get_year_history(product: dict):
    """Generate 365 days of price history across all platforms."""
    history = []
    today = datetime.utcnow()
    for days_ago in range(365, -1, -7):  # weekly points for a compact 1-year series
        date = today - timedelta(days=days_ago)
        prices = get_platform_prices(product, on_date=date)
        for p in prices:
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "platform": p["platform"],
                "price": p["price"],
            })
    return history


def generate_alert_for_product(product: dict):
    """AI-style alert generation based on simulated trend."""
    today_prices = get_platform_prices(product)
    yesterday_prices = get_platform_prices(product, on_date=datetime.utcnow() - timedelta(days=1))

    best_today = min(today_prices, key=lambda x: x["price"])
    best_yesterday = min(yesterday_prices, key=lambda x: x["price"])

    diff = best_today["price"] - best_yesterday["price"]
    pct = (diff / best_yesterday["price"]) * 100 if best_yesterday["price"] else 0

    if pct <= -3:
        return {
            "type": "price_drop",
            "message": f"Price dropped {abs(pct):.1f}% on {best_today['platform']} — good time to buy.",
            "platform": best_today["platform"],
            "price": best_today["price"],
        }
    elif pct >= 3:
        return {
            "type": "rising",
            "message": f"Price rising {pct:.1f}% on {best_today['platform']} — consider buying soon.",
            "platform": best_today["platform"],
            "price": best_today["price"],
        }
    else:
        return {
            "type": "stable",
            "message": f"Price stable on {best_today['platform']}.",
            "platform": best_today["platform"],
            "price": best_today["price"],
        }
