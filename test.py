from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    cross_encoder_rerank,
    rerank_results,
    get_target_section,
    expand_query,
)

from backend.app.services.retrieval import search_documents as dense_search
from backend.app.services.bm25 import search_bm25


# ============================================================
# TEST 16 ONLY
# ============================================================

query = "What punishment is prescribed for dacoity under the BNS?"

EXPECTED_SECTION = "310"

print("=" * 70)
print("TEST 16 — RETRIEVAL TRACE")
print("=" * 70)

offence, target_section = get_target_section(query)

print("\nQuery:", query)
print("Detected offence:", offence)
print("Target section:", target_section)
print("Expected section:", EXPECTED_SECTION)


# ============================================================
# QUERY EXPANSION
# ============================================================

expanded_query = expand_query(query)

print("\n" + "=" * 70)
print("EXPANDED QUERY")
print("=" * 70)

print(expanded_query)


# ============================================================
# DENSE RETRIEVAL
# ============================================================

print("\n" + "=" * 70)
print("DENSE RETRIEVAL")
print("=" * 70)

dense_results = dense_search(
    expanded_query,
    k=30,
    target_section=target_section
)

for rank, result in enumerate(dense_results, 1):

    section = str(
        result.get("metadata", {}).get("section", "")
    )

    print(f"{rank:02d}. Section {section}")


# ============================================================
# BM25
# ============================================================

print("\n" + "=" * 70)
print("BM25 RETRIEVAL")
print("=" * 70)

bm25_results = search_bm25(
    expanded_query,
    k=30
)

for rank, result in enumerate(bm25_results, 1):

    section = str(
        result.get("metadata", {}).get("section", "")
    )

    print(f"{rank:02d}. Section {section}")


# ============================================================
# CHECK §310 BEFORE RRF
# ============================================================

print("\n" + "=" * 70)
print("SECTION 310 BEFORE RRF")
print("=" * 70)

dense_310 = [
    (rank, r)
    for rank, r in enumerate(dense_results, 1)
    if str(r.get("metadata", {}).get("section", "")) == EXPECTED_SECTION
]

bm25_310 = [
    (rank, r)
    for rank, r in enumerate(bm25_results, 1)
    if str(r.get("metadata", {}).get("section", "")) == EXPECTED_SECTION
]

print(
    "Dense §310:",
    dense_310[0][0] if dense_310 else "NOT FOUND"
)

print(
    "BM25 §310:",
    bm25_310[0][0] if bm25_310 else "NOT FOUND"
)


# ============================================================
# RRF
# ============================================================

print("\n" + "=" * 70)
print("RRF")
print("=" * 70)

rrf_results = reciprocal_rank_fusion(
    dense_results,
    bm25_results
)

print("Total RRF candidates:", len(rrf_results))


for rank, result in enumerate(rrf_results, 1):

    section = str(
        result.get("metadata", {}).get("section", "")
    )

    if section == EXPECTED_SECTION:

        print(f"\nFOUND §310 at RRF rank {rank}")

        print(
            "RRF score:",
            result.get("rrf_score")
        )

        print(
            "Text:",
            result.get("text", "")[:1500]
        )


# ============================================================
# RRF RANKING
# ============================================================

print("\nRRF ranking:")

for rank, result in enumerate(rrf_results, 1):

    section = str(
        result.get("metadata", {}).get("section", "")
    )

    print(
        f"{rank:02d}. Section {section} "
        f"RRF={result.get('rrf_score')}"
    )


# ============================================================
# CROSS ENCODER
# ============================================================

print("\n" + "=" * 70)
print("CROSS-ENCODER STAGE")
print("=" * 70)

reranked = cross_encoder_rerank(
    query,
    rrf_results,
    top_k=40
)

found = False

for rank, result in enumerate(reranked, 1):

    section = str(
        result.get("metadata", {}).get("section", "")
    )

    if section == EXPECTED_SECTION:

        found = True

        print("\n§310 survived into cross-encoder.")

        print(
            "Cross-encoder rank:",
            rank
        )

        print(
            "Cross-encoder score:",
            result.get("cross_encoder_score")
        )

        print(
            "Text:",
            result.get("text", "")[:1500]
        )


if not found:

    print(
        "\n§310 DID NOT reach the cross-encoder."
    )


# ============================================================
# FINAL LEGAL RERANK
# ============================================================

final_results = rerank_results(
    query=query,
    results=reranked,
    target_section=target_section,
    detected_offence=offence
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("FINAL RANKING")
print("=" * 70)

for rank, result in enumerate(
    final_results[:10],
    1
):

    section = str(
        result.get("metadata", {}).get("section", "")
    )

    print(
        f"{rank:02d}. Section {section} | "
        f"RRF={result.get('rrf_score', 0):.6f} | "
        f"CE={result.get('cross_encoder_score', 0):.6f} | "
        f"Final={result.get('rerank_score', 0):.6f}"
    )


# ============================================================
# PASS / FAIL
# ============================================================

top_section = str(
    final_results[0]
    .get("metadata", {})
    .get("section", "")
)

print("\n" + "=" * 70)
print("TEST 16 RESULT")
print("=" * 70)

print("Expected:", EXPECTED_SECTION)
print("Predicted:", top_section)

if top_section == EXPECTED_SECTION:
    print("\nPASS")
else:
    print("\nFAIL")