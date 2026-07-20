from fastapi import FastAPI
from backend.app.routers import legal 

app = FastAPI(title="LegalRAG API")

app.include_router(legal.router)


@app.get("/")
def home():
    return {
        "project": "LegalRAG",
        "status": "Running"
    }