from backend.app.services.legal_pipeline import (
    answer_legal_query
)


# ============================================================
# TEST QUERY
# ============================================================

QUERY = "What is the punishment for cheating?"


# ============================================================
# RUN PIPELINE
# ============================================================

result = answer_legal_query(
    QUERY
)


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("FINAL LEGALRAG RESULT")
print("=" * 70)

print("\nQUESTION:")
print(result["query"])

print("\nANSWER:")
print(result["answer"])

print("\nSECTIONS:")
print(result["sections"])

print("\nSOURCES:")

for source in result["sources"]:

    print(
        f"- {source['document']} | "
        f"Section {source['section']} | "
        f"Year {source['year']}"
    )

print("\nGROUNDED:")
print(result["grounded"])

print("\nCITATION VERIFICATION:")
print(
    result[
        "citation_verification"
    ]
)

print("\nRETRIEVED EVIDENCE COUNT:")
print(
    result[
        "retrieval_count"
    ]
)

print("\n" + "=" * 70)
print("END-TO-END TEST COMPLETE")
print("=" * 70)