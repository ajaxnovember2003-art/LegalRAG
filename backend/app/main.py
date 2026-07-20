from fastapi import FastAPI

app = FastAPI(title="LegalRAG API")


@app.get("/")
def home():
    return {
        "project": "LegalRAG",
        "status": "Running"
    }