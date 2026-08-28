from backend.app.services.hybrid_retrieval import hybrid_search


query = "What is the punishment for murder?"


print("\nQUERY:")
print(query)


results = hybrid_search(
    query,
    k=5
)


print("\nFINAL RERANKED RESULTS")


for rank, result in enumerate(results, start=1):

    print("\n====================")
    print(f"RESULT {rank}")
    print("====================")

    print(
        result["metadata"]
    )

    print(
        result["text"]
    )

    print(
        "RRF Score:",
        result["rrf_score"]
    )

    print(
        "Rerank Score:",
        result["rerank_score"]
    )