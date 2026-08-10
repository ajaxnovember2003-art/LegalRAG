from backend.app.services.bm25 import search_bm25


query = "What is the punishment for murder?"


results = search_bm25(
    query,
    k=5
)


print("\nQUERY:")
print(query)

print("\nBM25 RESULTS")


for i, result in enumerate(results, 1):

    print("\n====================")
    print("RESULT", i)
    print("====================")

    print("Index:", result["index"])
    print("Score:", result["score"])