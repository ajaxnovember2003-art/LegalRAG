from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    cross_encoder_rerank,
    rerank_results,
    get_target_section,
)

from backend.app.services.retrieval import search_documents as dense_search
from backend.app.services.bm25 import search_bm25


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [

    # --------------------------------------------------------
    # Direct offence queries
    # --------------------------------------------------------

    {
        "query": "What is the punishment for wrongful restraint?",
        "expected": "126",
    },

    {
        "query": "What is the punishment for wrongful confinement?",
        "expected": "127",
    },

    {
        "query": "What is the punishment for theft?",
        "expected": "303",
    },

    {
        "query": "What is the punishment for robbery?",
        "expected": "309",
    },

    {
        "query": "What is the punishment for dacoity?",
        "expected": "310",
    },

    {
        "query": "What is the punishment for murder?",
        "expected": "103",
    },

    {
        "query": "What is the punishment for culpable homicide?",
        "expected": "105",
    },

    {
        "query": "What is the punishment for attempt to murder?",
        "expected": "109",
    },

    {
        "query": "What is the punishment for cheating?",
        "expected": "318",
    },

    {
        "query": "What is the punishment for extortion?",
        "expected": "308",
    },

    # --------------------------------------------------------
    # Natural language variations
    # --------------------------------------------------------

    {
        "query": "What happens if someone prevents another person from going where they have a legal right to go?",
        "expected": "126",
    },

    {
        "query": "Which BNS provision deals with stopping a person from proceeding in a direction they have the right to take?",
        "expected": "126",
    },

    {
        "query": "What offence is committed when a person is prevented from leaving a place?",
        "expected": "127",
    },

    {
        "query": "Which section deals with taking someone's movable property dishonestly?",
        "expected": "303",
    },

    {
        "query": "Which BNS section deals with robbery?",
        "expected": "309",
    },

    {
        "query": "Which section applies when five or more persons jointly commit robbery?",
        "expected": "310",
    },

    # --------------------------------------------------------
    # Punishment-focused queries
    # --------------------------------------------------------

    {
        "query": "How long can a person be imprisoned for wrongful restraint?",
        "expected": "126",
    },

    {
        "query": "Can a fine be imposed for wrongful restraint?",
        "expected": "126",
    },

    {
        "query": "What imprisonment applies to wrongful confinement?",
        "expected": "127",
    },

    {
        "query": "What punishment is prescribed for cheating under the BNS?",
        "expected": "318",
    },

]


# ============================================================
# RUN ONE TEST
# ============================================================

def run_test(test_number, test_case):

    query = test_case["query"]
    expected = str(test_case["expected"])

    print("\n" + "=" * 80)
    print(f"TEST {test_number}")
    print("=" * 80)

    print("Query:")
    print(query)

    # --------------------------------------------------------
    # Detect offence / target
    # --------------------------------------------------------

    offence, target_section = get_target_section(query)

    print("\nDetected offence:", offence)
    print("Expected section:", expected)
    print("Detected target:", target_section)

    # --------------------------------------------------------
    # Dense retrieval
    # --------------------------------------------------------

    dense_results = dense_search(
        query,
        k=30,
        target_section=target_section
    )

    # --------------------------------------------------------
    # BM25
    # --------------------------------------------------------

    bm25_results = search_bm25(
        query,
        k=120
    )

    # --------------------------------------------------------
    # RRF
    # --------------------------------------------------------

    rrf_results = reciprocal_rank_fusion(
        dense_results,
        bm25_results
    )

    # --------------------------------------------------------
    # Cross encoder
    # --------------------------------------------------------

    reranked = cross_encoder_rerank(
        query,
        rrf_results,
        target_section=target_section,
        top_k=40
    )

    # --------------------------------------------------------
    # Legal reranking
    # --------------------------------------------------------

    final_results = rerank_results(
        query=query,
        results=reranked,
        target_section=target_section,
        detected_offence=offence
    )

    # --------------------------------------------------------
    # Find expected section ranks
    # --------------------------------------------------------

    dense_rank = None
    bm25_rank = None
    rrf_rank = None
    ce_rank = None
    final_rank = None

    for rank, result in enumerate(dense_results, 1):

        section = str(
            result.get("metadata", {}).get("section", "")
        ).strip()

        if section == expected:
            dense_rank = rank
            break

    for rank, result in enumerate(bm25_results, 1):

        section = str(
            result.get("metadata", {}).get("section", "")
        ).strip()

        if section == expected:
            bm25_rank = rank
            break

    for rank, result in enumerate(rrf_results, 1):

        section = str(
            result.get("metadata", {}).get("section", "")
        ).strip()

        if section == expected:
            rrf_rank = rank
            break

    for rank, result in enumerate(reranked, 1):

        section = str(
            result.get("metadata", {}).get("section", "")
        ).strip()

        if section == expected:
            ce_rank = rank
            break

    for rank, result in enumerate(final_results, 1):

        section = str(
            result.get("metadata", {}).get("section", "")
        ).strip()

        if section == expected:
            final_rank = rank
            break

    # --------------------------------------------------------
    # Top result
    # --------------------------------------------------------

    top_section = None

    if final_results:

        top_section = str(
            final_results[0]
            .get("metadata", {})
            .get("section", "")
        ).strip()

    passed = top_section == expected

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("RESULT")
    print("-" * 80)

    print("Dense rank :", dense_rank)
    print("BM25 rank  :", bm25_rank)
    print("RRF rank   :", rrf_rank)
    print("CE rank    :", ce_rank)
    print("Final rank :", final_rank)

    print("\nTop final section:", top_section)
    print("Expected section :", expected)

    if passed:
        print("\nPASS")
    else:
        print("\nFAIL")

        print("\nTop 5 final results:")

        for rank, result in enumerate(
            final_results[:5],
            1
        ):

            section = str(
                result.get(
                    "metadata",
                    {}
                ).get(
                    "section",
                    ""
                )
            ).strip()

            print(
                f"{rank:02d}. Section {section} "
                f"Final={result.get('rerank_score', 0):.6f}"
            )

    return {
        "query": query,
        "expected": expected,
        "dense_rank": dense_rank,
        "bm25_rank": bm25_rank,
        "rrf_rank": rrf_rank,
        "ce_rank": ce_rank,
        "final_rank": final_rank,
        "top_section": top_section,
        "passed": passed,
    }


# ============================================================
# MAIN
# ============================================================

results = []

print("\n")
print("=" * 80)
print("LEGAL RAG — RETRIEVAL STRESS TEST")
print("=" * 80)

for i, test_case in enumerate(
    TEST_CASES,
    1
):

    try:

        result = run_test(
            i,
            test_case
        )

        results.append(result)

    except Exception as e:

        print("\nTEST ERROR:")
        print(e)

        results.append({
            "query": test_case["query"],
            "expected": str(test_case["expected"]),
            "passed": False,
            "error": str(e),
        })


# ============================================================
# SUMMARY
# ============================================================

print("\n\n")
print("=" * 80)
print("FINAL STRESS TEST SUMMARY")
print("=" * 80)

passed = sum(
    1
    for r in results
    if r.get("passed")
)

total = len(results)

print(
    f"\nAccuracy: {passed}/{total} "
    f"({passed / total * 100:.2f}%)"
)

print("\nDetailed results:")

for i, result in enumerate(
    results,
    1
):

    status = "PASS" if result.get("passed") else "FAIL"

    print(
        f"{i:02d}. {status} | "
        f"Expected §{result.get('expected')} | "
        f"Final rank={result.get('final_rank')} | "
        f"Top=§{result.get('top_section')}"
    )

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
