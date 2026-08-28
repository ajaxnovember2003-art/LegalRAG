from backend.app.services.hybrid_retrieval import hybrid_search

query = "What is the punishment for wrongful restraint?"

results = hybrid_search(query)

print("\n" + "=" * 70)
print("WRONGFUL RESTRAINT DEBUG")
print("=" * 70)

for i, result in enumerate(results[:10], start=1):
    print(f"\nRESULT {i}")
    print("-" * 50)

    print("Section:", result.get("metadata", {}).get("section"))
    print("RRF:", result.get("rrf_score"))
    print("Cross Encoder:", result.get("cross_encoder_score"))
    print("Rerank:", result.get("rerank_score"))
    print("Exact Match:", result.get("exact_section_match"))

    print("\nTEXT:")
    print(result.get("text", "")[:1500])