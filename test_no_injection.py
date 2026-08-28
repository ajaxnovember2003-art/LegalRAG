import time

from backend.app.services.hybrid_retrieval import (
    dense_search,
    search_bm25,
    reciprocal_rank_fusion,
    cross_encoder_rerank,
    rerank_results,
    expand_query,
    extract_offence,
    get_target_section,
)


# ============================================================
# CONFIGURATION
# ============================================================

DENSE_K = 30
BM25_K = 50

RRF_TOP_K = 20
CE_TOP_K = 20


# ============================================================
# TEST DATA
# ============================================================

TEST_CASES = [

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
        "query": "What is the punishment for cheating?",
        "expected": "318",
    },

    {
        "query": "What imprisonment applies to wrongful confinement?",
        "expected": "127",
    },

    {
        "query": "What is the punishment for wrongful restraint?",
        "expected": "126",
    },

    {
        "query": "What is the punishment for murder?",
        "expected": "103",
    },

    {
        "query": "What punishment is prescribed for culpable homicide?",
        "expected": "105",
    },

    {
        "query": "What is the punishment for attempt to murder?",
        "expected": "109",
    },

    {
        "query": "What is the punishment for extortion?",
        "expected": "308",
    },
]


# ============================================================
# SECTION EXTRACTION
# ============================================================

def get_section(result):

    metadata = result.get(
        "metadata",
        {}
    )

    section = metadata.get(
        "section"
    )

    if section is None:
        return None

    return str(
        section
    ).strip()


# ============================================================
# FIND TARGET RANK
# ============================================================

def find_target_rank(
    results,
    target_section
):

    target_section = str(
        target_section
    ).strip()

    for rank, result in enumerate(
        results,
        start=1
    ):

        section = get_section(
            result
        )

        if section == target_section:

            return rank

    return None


# ============================================================
# TOP-K HIT
# ============================================================

def hit_at_k(
    results,
    target_section,
    k
):

    rank = find_target_rank(
        results,
        target_section
    )

    if rank is None:
        return False

    return rank <= k


# ============================================================
# RECIPROCAL RANK
# ============================================================

def reciprocal_rank(
    results,
    target_section
):

    rank = find_target_rank(
        results,
        target_section
    )

    if rank is None:
        return 0.0

    return 1.0 / rank


# ============================================================
# RUN TEST
# ============================================================

def run_test(
    test_number,
    query,
    expected_section
):

    print("\n")
    print("=" * 70)
    print(f"TEST {test_number}")
    print("=" * 70)

    print(
        f"Query: {query}"
    )

    print(
        f"Expected section: "
        f"{expected_section}"
    )

    # --------------------------------------------------------
    # OFFENCE DETECTION
    # --------------------------------------------------------

    detected_offence, target_section = (
        get_target_section(query)
    )

    print(
        f"\nDetected offence: "
        f"{detected_offence}"
    )

    print(
        f"Evaluation target: "
        f"{target_section}"
    )

    # --------------------------------------------------------
    # QUERY EXPANSION
    # --------------------------------------------------------

    expanded_query = expand_query(
        query
    )

    print(
        "\nExpanded Query:"
    )

    print(
        expanded_query
    )

    # IMPORTANT CHECK
    if str(expected_section) in expanded_query:

        print(
            "\nWARNING: EXPECTED SECTION "
            "FOUND IN EXPANDED QUERY!"
        )

    else:

        print(
            "\nNo target section leakage detected."
        )

    # ========================================================
    # DENSE
    # ========================================================

    print("\n" + "-" * 70)
    print("DENSE RETRIEVAL")
    print("-" * 70)

    dense_results = dense_search(
        expanded_query,
        k=DENSE_K
    )

    dense_rank = find_target_rank(
        dense_results,
        expected_section
    )

    print(
        f"Dense results: "
        f"{len(dense_results)}"
    )

    print(
        f"Dense target rank: "
        f"{dense_rank}"
    )

    # ========================================================
    # BM25
    # ========================================================

    print("\n" + "-" * 70)
    print("BM25 RETRIEVAL")
    print("-" * 70)

    bm25_results = search_bm25(
        expanded_query,
        k=BM25_K
    )

    bm25_rank = find_target_rank(
        bm25_results,
        expected_section
    )

    print(
        f"BM25 results: "
        f"{len(bm25_results)}"
    )

    print(
        f"BM25 target rank: "
        f"{bm25_rank}"
    )

    # ========================================================
    # RRF
    # ========================================================

    print("\n" + "-" * 70)
    print("RECIPROCAL RANK FUSION")
    print("-" * 70)

    rrf_results = reciprocal_rank_fusion(
        dense_results,
        bm25_results
    )

    # Only evaluate the first RRF_TOP_K
    rrf_top = rrf_results[
        :RRF_TOP_K
    ]

    rrf_rank = find_target_rank(
        rrf_results,
        expected_section
    )

    print(
        f"Total RRF results: "
        f"{len(rrf_results)}"
    )

    print(
        f"RRF target rank: "
        f"{rrf_rank}"
    )

    # ========================================================
    # CROSS ENCODER
    # ========================================================

    print("\n" + "-" * 70)
    print("CROSS-ENCODER RERANKING")
    print("-" * 70)

    ce_results = cross_encoder_rerank(
        query=expanded_query,
        results=rrf_results,
        top_k=CE_TOP_K
    )

    ce_rank = find_target_rank(
        ce_results,
        expected_section
    )

    print(
        f"Cross-Encoder results: "
        f"{len(ce_results)}"
    )

    print(
        f"Cross-Encoder target rank: "
        f"{ce_rank}"
    )

    # ========================================================
    # LEGAL-AWARE RERANKING
    # ========================================================

    print("\n" + "-" * 70)
    print("LEGAL-AWARE RERANKING")
    print("-" * 70)

    final_results = rerank_results(
        query=query,
        results=ce_results,
        detected_offence=detected_offence
    )

    final_rank = find_target_rank(
        final_results,
        expected_section
    )

    # ========================================================
    # FINAL PREDICTION
    # ========================================================

    if final_results:

        predicted_section = get_section(
            final_results[0]
        )

    else:

        predicted_section = None

    # ========================================================
    # METRICS
    # ========================================================

    result = {

        "pass": (
            predicted_section
            == str(expected_section)
        ),

        "dense_rank": dense_rank,

        "bm25_rank": bm25_rank,

        "rrf_rank": rrf_rank,

        "ce_rank": ce_rank,

        "final_rank": final_rank,

        "dense_hit_1": hit_at_k(
            dense_results,
            expected_section,
            1
        ),

        "dense_hit_3": hit_at_k(
            dense_results,
            expected_section,
            3
        ),

        "dense_hit_5": hit_at_k(
            dense_results,
            expected_section,
            5
        ),

        "dense_hit_10": hit_at_k(
            dense_results,
            expected_section,
            10
        ),

        "bm25_hit_1": hit_at_k(
            bm25_results,
            expected_section,
            1
        ),

        "bm25_hit_3": hit_at_k(
            bm25_results,
            expected_section,
            3
        ),

        "bm25_hit_5": hit_at_k(
            bm25_results,
            expected_section,
            5
        ),

        "bm25_hit_10": hit_at_k(
            bm25_results,
            expected_section,
            10
        ),

        "rrf_hit_1": hit_at_k(
            rrf_results,
            expected_section,
            1
        ),

        "rrf_hit_3": hit_at_k(
            rrf_results,
            expected_section,
            3
        ),

        "rrf_hit_5": hit_at_k(
            rrf_results,
            expected_section,
            5
        ),

        "rrf_hit_10": hit_at_k(
            rrf_results,
            expected_section,
            10
        ),

        "ce_hit_1": hit_at_k(
            ce_results,
            expected_section,
            1
        ),

        "ce_hit_3": hit_at_k(
            ce_results,
            expected_section,
            3
        ),

        "ce_hit_5": hit_at_k(
            ce_results,
            expected_section,
            5
        ),

        "ce_hit_10": hit_at_k(
            ce_results,
            expected_section,
            10
        ),

        "final_hit_1": hit_at_k(
            final_results,
            expected_section,
            1
        ),

        "final_hit_3": hit_at_k(
            final_results,
            expected_section,
            3
        ),

        "final_hit_5": hit_at_k(
            final_results,
            expected_section,
            5
        ),

        "final_hit_10": hit_at_k(
            final_results,
            expected_section,
            10
        ),

        "final_rr": reciprocal_rank(
            final_results,
            expected_section
        ),
    }

    # ========================================================
    # PRINT
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(
        f"Expected section : "
        f"{expected_section}"
    )

    print(
        f"Predicted section: "
        f"{predicted_section}"
    )

    print(
        f"Dense rank       : "
        f"{dense_rank}"
    )

    print(
        f"BM25 rank        : "
        f"{bm25_rank}"
    )

    print(
        f"RRF rank         : "
        f"{rrf_rank}"
    )

    print(
        f"Cross-Encoder    : "
        f"{ce_rank}"
    )

    print(
        f"Final rank       : "
        f"{final_rank}"
    )

    print(
        f"MRR contribution : "
        f"{result['final_rr']:.4f}"
    )

    if result["pass"]:

        print("\nPASS")

    else:

        print("\nFAIL")

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "LEGAL RAG — PURE RETRIEVAL EVALUATION"
    )
    print("=" * 70)

    print(
        "\nTARGET INJECTION: DISABLED"
    )

    print(
        "SECTION NUMBERS ARE NOT ADDED "
        "TO EVALUATION QUERIES."
    )

    print(
        "NO EXACT-SECTION BOOST IS USED."
    )

    print(
        "THE CORRECT SECTION MUST BE "
        "RETRIEVED NATURALLY."
    )

    results = []

    start_time = time.time()

    # --------------------------------------------------------
    # TESTS
    # --------------------------------------------------------

    for i, test in enumerate(
        TEST_CASES,
        start=1
    ):

        result = run_test(
            test_number=i,
            query=test["query"],
            expected_section=test["expected"]
        )

        results.append(
            result
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    total = len(
        results
    )

    # --------------------------------------------------------
    # TOP-1
    # --------------------------------------------------------

    passed = sum(
        r["pass"]
        for r in results
    )

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    # --------------------------------------------------------
    # HIT@K
    # --------------------------------------------------------

    def percentage(
        key
    ):

        return (
            sum(
                r[key]
                for r in results
            )
            / total
            * 100
        )

    # --------------------------------------------------------
    # MRR
    # --------------------------------------------------------

    mrr = (
        sum(
            r["final_rr"]
            for r in results
        )
        / total
        if total
        else 0
    )

    elapsed = (
        time.time()
        - start_time
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n\n")
    print("=" * 70)
    print(
        "FINAL EVALUATION SUMMARY"
    )
    print("=" * 70)

    print(
        f"Total tests : {total}"
    )

    print(
        f"Top-1       : "
        f"{accuracy:.2f}%"
    )

    print(
        f"MRR         : "
        f"{mrr:.4f}"
    )

    print("\n")
    print("DENSE RETRIEVAL")

    print(
        f"Hit@1  : "
        f"{percentage('dense_hit_1'):.2f}%"
    )

    print(
        f"Hit@3  : "
        f"{percentage('dense_hit_3'):.2f}%"
    )

    print(
        f"Hit@5  : "
        f"{percentage('dense_hit_5'):.2f}%"
    )

    print(
        f"Hit@10 : "
        f"{percentage('dense_hit_10'):.2f}%"
    )

    print("\n")
    print("BM25 RETRIEVAL")

    print(
        f"Hit@1  : "
        f"{percentage('bm25_hit_1'):.2f}%"
    )

    print(
        f"Hit@3  : "
        f"{percentage('bm25_hit_3'):.2f}%"
    )

    print(
        f"Hit@5  : "
        f"{percentage('bm25_hit_5'):.2f}%"
    )

    print(
        f"Hit@10 : "
        f"{percentage('bm25_hit_10'):.2f}%"
    )

    print("\n")
    print("RRF")

    print(
        f"Hit@1  : "
        f"{percentage('rrf_hit_1'):.2f}%"
    )

    print(
        f"Hit@3  : "
        f"{percentage('rrf_hit_3'):.2f}%"
    )

    print(
        f"Hit@5  : "
        f"{percentage('rrf_hit_5'):.2f}%"
    )

    print(
        f"Hit@10 : "
        f"{percentage('rrf_hit_10'):.2f}%"
    )

    print("\n")
    print("CROSS-ENCODER")

    print(
        f"Hit@1  : "
        f"{percentage('ce_hit_1'):.2f}%"
    )

    print(
        f"Hit@3  : "
        f"{percentage('ce_hit_3'):.2f}%"
    )

    print(
        f"Hit@5  : "
        f"{percentage('ce_hit_5'):.2f}%"
    )

    print(
        f"Hit@10 : "
        f"{percentage('ce_hit_10'):.2f}%"
    )

    print("\n")
    print("FINAL LEGAL RERANKER")

    print(
        f"Hit@1  : "
        f"{percentage('final_hit_1'):.2f}%"
    )

    print(
        f"Hit@3  : "
        f"{percentage('final_hit_3'):.2f}%"
    )

    print(
        f"Hit@5  : "
        f"{percentage('final_hit_5'):.2f}%"
    )

    print(
        f"Hit@10 : "
        f"{percentage('final_hit_10'):.2f}%"
    )

    print("\n")
    print(
        f"Execution time: "
        f"{elapsed:.2f} seconds"
    )

    # ========================================================
    # PER-TEST RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("PER-TEST RESULTS")
    print("=" * 70)

    for i, result in enumerate(
        results,
        start=1
    ):

        status = (
            "PASS"
            if result["pass"]
            else "FAIL"
        )

        print(
            f"{i:02d}. {status} | "
            f"Dense={result['dense_rank']} | "
            f"BM25={result['bm25_rank']} | "
            f"RRF={result['rrf_rank']} | "
            f"CE={result['ce_rank']} | "
            f"Final={result['final_rank']}"
        )

    print("\n")
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()