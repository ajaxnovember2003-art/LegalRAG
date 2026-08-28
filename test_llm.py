from backend.app.services.retrieval import search_documents
from backend.app.services.llm import generate_answer


query = "What is the punishment for murder?"

context = search_documents(query, k=5)

answer = generate_answer(query, context)

print("\n# LLM ANSWER\n")
print(answer)