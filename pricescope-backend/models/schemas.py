from pydantic import BaseModel
from typing import List, Optional


class PlatformPrice(BaseModel):
    platform: str
    price: float
    url: Optional[str] = None


class Product(BaseModel):
    id: str
    name: str
    category: str
    base_price: float
    image: Optional[str] = None


class ProductWithPrices(Product):
    platform_prices: List[PlatformPrice]
    best_price: float
    best_platform: str


class HistoryPoint(BaseModel):
    date: str
    platform: str
    price: float


class Alert(BaseModel):
    product_id: str
    product_name: str
    type: str  # "price_drop" | "all_time_low" | "rising" | "predicted_sale"
    message: str
    platform: Optional[str] = None
    price: Optional[float] = None
