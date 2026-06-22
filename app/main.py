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
