from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LegalQuery(BaseModel):
    question: str


@router.post("/ask")
def ask_question(query: LegalQuery):
    return {
        "question": query.question,
        "answer": "LegalRAG response module will be connected here.",
        "status": "Query received successfully."
    }