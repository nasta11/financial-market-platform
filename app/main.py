from sklearn.linear_model import LinearRegression
import pandas as pd
import plotly.express as px
from fastapi.responses import HTMLResponse
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
@app.get("/chart/{ticker}", response_class=HTMLResponse)
def get_price_chart(ticker: str, db: Session = Depends(get_db)):
    prices = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker.upper())
        .order_by(StockPrice.date)
        .all()
    )

    if not prices:
        return "<h3>No data found</h3>"

    data = [
        {
            "date": p.date,
            "close_price": p.close_price
        }
        for p in prices
    ]

    df = pd.DataFrame(data)

    fig = px.line(
        df,
        x="date",
        y="close_price",
        title=f"{ticker.upper()} Stock Price"
    )

    return fig.to_html(full_html=True)
@app.get("/tickers")
def get_tickers(db: Session = Depends(get_db)):
    tickers = (
        db.query(StockPrice.ticker)
        .distinct()
        .all()
    )

    return [ticker[0] for ticker in tickers]
@app.get("/dashboard/{ticker}", response_class=HTMLResponse)
def dashboard(ticker: str, db: Session = Depends(get_db)):

    prices = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker.upper())
        .order_by(StockPrice.date)
        .all()
    )

    if not prices:
        return "<h1>Данные не найдены</h1>"

    df = pd.DataFrame([
        {
            "date": p.date,
            "close_price": p.close_price
        }
        for p in prices
    ])

    fig = px.line(
        df,
        x="date",
        y="close_price",
        title=f"График изменения цены закрытия: {ticker.upper()}"
    )

    avg_price = round(df["close_price"].mean(), 2)
    max_price = round(df["close_price"].max(), 2)
    min_price = round(df["close_price"].min(), 2)

    close_prices = df["close_price"].tolist()
    X = [[i] for i in range(len(close_prices))]
    y = close_prices

    model = LinearRegression()
    model.fit(X, y)

    predicted_price = model.predict([[len(close_prices)]])[0]
    last_price = close_prices[-1]
    expected_change = predicted_price - last_price

    if expected_change > 1:
        recommendation = "ПОКУПАТЬ"
    elif expected_change < -1:
        recommendation = "ПРОДАВАТЬ"
    else:
        recommendation = "ДЕРЖАТЬ"

    return f"""
    <html>
    <head>
        <title>Панель анализа финансового актива</title>
    </head>
    <body style="font-family: Arial; margin: 40px;">
        <h1>Платформа анализа финансовых рынков</h1>
        <h2>Аналитическая панель: {ticker.upper()}</h2>

        <h3>Основные показатели</h3>
        <ul>
            <li><b>Средняя цена закрытия:</b> {avg_price}</li>
            <li><b>Максимальная цена закрытия:</b> {max_price}</li>
            <li><b>Минимальная цена закрытия:</b> {min_price}</li>
        </ul>

        <h3>Прогнозирование</h3>
        <ul>
            <li><b>Последняя цена:</b> {round(last_price, 2)}</li>
            <li><b>Прогноз на следующий торговый день:</b> {round(predicted_price, 2)}</li>
            <li><b>Ожидаемое изменение:</b> {round(expected_change, 2)}</li>
            <li><b>Рекомендация системы:</b> {recommendation}</li>
        </ul>

        <h3>График изменения цены закрытия</h3>
        {fig.to_html(full_html=False)}
    </body>
    </html>
    """
