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


def _seasonal_factor(month: int) -> float:
    """
    Approximate Indian e-commerce seasonal pricing pattern:
    - Oct/Nov: festival season (Diwali) -> biggest discounts
    - Jan: New Year sales -> moderate discount
    - Jun/Jul: monsoon/mid-year sales -> small discount
    - Mar: financial year-end -> slight discount
    - Other months: baseline, slightly higher
    """
    seasonal_map = {
        1: -0.05,   # Jan - New Year sale
        2: 0.0,
        3: -0.03,   # Mar - FY-end clearance
        4: 0.0,
        5: 0.0,
        6: -0.02,   # Jun - mid-year sale
        7: -0.02,   # Jul - mid-year sale
        8: 0.0,
        9: 0.02,    # Sep - pre-festival price creep
        10: -0.10,  # Oct - Diwali/festival season
        11: -0.08,  # Nov - festival season continues
        12: -0.04,  # Dec - year-end sale
    }
    return seasonal_map.get(month, 0.0)


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


def _internal_seasonal_price(product: dict, on_date: datetime) -> float:
    """
    INTERNAL/OWNER-ONLY price calculation used solely by the seasonal
    analysis endpoint. Completely separate from get_platform_prices(),
    which powers the public shopper-facing Products/Compare/Dashboard
    pages — changes here never affect what customers see.
    """
    rng = _seeded_random(f"{product['id']}-internal-{on_date.strftime('%Y-%m-%d')}")
    daily_fluctuation = rng.uniform(-0.04, 0.04)
    seasonal = _seasonal_factor(on_date.month)
    price = product["base_price"] * (1 + daily_fluctuation + seasonal)
    return round(price / 10) * 10


MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


def get_seasonal_analysis(product: dict):
    """
    Internal owner-facing analysis: averages a simulated best price per
    month across the last year using an isolated internal price model
    (separate from public pricing), identifies the cheapest and most
    expensive months, and writes a plain-language strategy note.
    """
    today = datetime.utcnow()
    monthly_best = {}

    for days_ago in range(365, -1, -7):
        date = today - timedelta(days=days_ago)
        price = _internal_seasonal_price(product, date)
        monthly_best.setdefault(date.month, []).append(price)

    monthly_avg = {
        m: round(sum(v) / len(v))
        for m, v in monthly_best.items()
    }

    if not monthly_avg:
        return None

    cheapest_month = min(monthly_avg, key=monthly_avg.get)
    priciest_month = max(monthly_avg, key=monthly_avg.get)
    overall_avg = round(sum(monthly_avg.values()) / len(monthly_avg))
    dip_pct = round((monthly_avg[priciest_month] - monthly_avg[cheapest_month]) / monthly_avg[priciest_month] * 100, 1)

    if dip_pct >= 12:
        strategy = (
            f"Strong seasonal swing detected ({dip_pct}% gap). Consider matching "
            f"competitor discounts in {MONTH_NAMES[cheapest_month-1]}, and protecting "
            f"margin in {MONTH_NAMES[priciest_month-1]} when demand/prices are naturally higher."
        )
    elif dip_pct >= 5:
        strategy = (
            f"Moderate seasonal pattern ({dip_pct}% gap). {MONTH_NAMES[cheapest_month-1]} "
            f"is the most price-competitive month — a good window for a targeted promotion."
        )
    else:
        strategy = "Prices are fairly stable year-round for this product — no strong seasonal window to plan around."

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "monthly_avg_best_price": {MONTH_NAMES[m-1]: v for m, v in sorted(monthly_avg.items())},
        "cheapest_month": MONTH_NAMES[cheapest_month-1],
        "priciest_month": MONTH_NAMES[priciest_month-1],
        "overall_avg_price": overall_avg,
        "seasonal_dip_pct": dip_pct,
        "strategy_note": strategy,
    }


def evaluate_owner_price(product: dict, proposed_price: float):
    """
    Takes a price the owner is considering and compares it against the
    product's seasonal pattern (current month's typical price, and the
    cheapest/priciest months) to produce a direct recommendation.
    """
    analysis = get_seasonal_analysis(product)
    if not analysis:
        return None

    current_month = MONTH_NAMES[datetime.utcnow().month - 1]
    current_month_avg = analysis["monthly_avg_best_price"].get(current_month, analysis["overall_avg_price"])
    diff = proposed_price - current_month_avg
    diff_pct = round((diff / current_month_avg) * 100, 1) if current_month_avg else 0

    if diff_pct <= -10:
        verdict = "below_seasonal_norm"
        message = (
            f"₹{proposed_price:,.0f} is {abs(diff_pct)}% below the typical {current_month} price "
            f"(₹{current_month_avg:,.0f}). This is an aggressive discount — good for clearing stock "
            f"or matching festival-season competitors, but check it doesn't erode margin unnecessarily."
        )
    elif diff_pct <= -3:
        verdict = "competitive"
        message = (
            f"₹{proposed_price:,.0f} is {abs(diff_pct)}% below the typical {current_month} price "
            f"(₹{current_month_avg:,.0f}) — a reasonable, competitive position for this time of year."
        )
    elif diff_pct < 3:
        verdict = "in_line"
        message = (
            f"₹{proposed_price:,.0f} is in line with the usual {current_month} price "
            f"(₹{current_month_avg:,.0f}) for this product. No strong seasonal pressure either way."
        )
    elif diff_pct < 12:
        verdict = "above_norm"
        message = (
            f"₹{proposed_price:,.0f} is {diff_pct}% above the typical {current_month} price "
            f"(₹{current_month_avg:,.0f}). Acceptable if quality/brand justifies it, but may lose price-sensitive buyers."
        )
    else:
        verdict = "overpriced"
        message = (
            f"₹{proposed_price:,.0f} is {diff_pct}% above the typical {current_month} price "
            f"(₹{current_month_avg:,.0f}) — this is significantly overpriced for the season and likely to hurt conversions."
        )

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "proposed_price": proposed_price,
        "current_month": current_month,
        "current_month_typical_price": round(current_month_avg),
        "diff_pct": diff_pct,
        "verdict": verdict,
        "message": message,
        "cheapest_month": analysis["cheapest_month"],
        "priciest_month": analysis["priciest_month"],
    }


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
