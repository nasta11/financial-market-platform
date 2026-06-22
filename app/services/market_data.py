import yfinance as yf
from app.models import StockPrice


def get_stock_info(ticker: str):
    stock = yf.Ticker(ticker)

    return {
        "ticker": ticker.upper(),
        "company": stock.info.get("longName"),
        "sector": stock.info.get("sector"),
        "current_price": stock.info.get("currentPrice")
    }


def load_stock_prices(ticker: str, db):
    ticker = ticker.upper()
    stock = yf.Ticker(ticker)
    data = stock.history(period="30d")

    count = 0

    for date, row in data.iterrows():
        price = StockPrice(
            ticker=ticker,
            date=date.date(),
            open_price=float(row["Open"]),
            high_price=float(row["High"]),
            low_price=float(row["Low"]),
            close_price=float(row["Close"]),
            volume=int(row["Volume"])
        )

        db.add(price)
        count += 1

    db.commit()

    return {
        "ticker": ticker,
        "loaded_records": count
    }
