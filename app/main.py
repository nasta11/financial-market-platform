from fastapi import FastAPI

app = FastAPI(
    title="Financial Market Analysis Platform",
    description="Prototype application for financial market data analysis",
    version="0.1.0"
)


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
