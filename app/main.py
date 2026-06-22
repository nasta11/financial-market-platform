from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Asset, StockPrice
from app.services.market_data import get_stock_info, load_stock_prices

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Market Analysis Platform",
    description="Prototype application for financial market data analysis",
    version="0.1.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Financial Market Platform is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/stocks/{ticker}")
def get_stock(ticker: str):
    return get_stock_info(ticker)


@app.post("/load/{ticker}")
def load_stock_data(ticker: str, db: Session = Depends(get_db)):
    return load_stock_prices(ticker, db)


@app.get("/prices/{ticker}")
def get_saved_prices(ticker: str, db: Session = Depends(get_db)):
    prices = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker.upper())
        .order_by(StockPrice.date)
        .all()
    )

    return [
        {
            "date": price.date,
            "open_price": price.open_price,
            "high_price": price.high_price,
            "low_price": price.low_price,
            "close_price": price.close_price,
            "volume": price.volume
        }
        for price in prices
    ]
@app.get("/analytics/{ticker}")
def get_analytics(ticker: str, db: Session = Depends(get_db)):
    prices = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker.upper())
        .all()
    )

    if not prices:
        return {"error": "No data found"}

    close_prices = [p.close_price for p in prices]
    volumes = [p.volume for p in prices]

    return {
        "ticker": ticker.upper(),
        "records": len(prices),
        "average_close_price": round(sum(close_prices) / len(close_prices), 2),
        "max_close_price": round(max(close_prices), 2),
        "min_close_price": round(min(close_prices), 2),
        "total_volume": sum(volumes)
    }
