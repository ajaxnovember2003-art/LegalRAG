from backend.app.services.retrieval import search_documents


query = "What is the punishment for murder?"


results = search_documents(
    query,
    k=5
)


print("\nQUERY:")
print(query)


print("\nTOP RESULTS")


for i, result in enumerate(results):

    print("\n====================")
    print("RESULT", i+1)
    print("====================")

    print(
        result["metadata"]
    )

    print(
        result["text"][:500]
    )

    print(
        "Score:",
        result["score"]
    )