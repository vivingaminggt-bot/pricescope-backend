from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import products, prices, history, alerts

app = FastAPI(
    title="PriceScope API",
    description="AI-powered e-commerce price comparison backend",
    version="1.0.0",
)

# Allow your frontend (Render static site) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend URL after testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(prices.router, prefix="/api/prices", tags=["Prices"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])


@app.get("/")
def root():
    return {"status": "ok", "service": "PriceScope API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
