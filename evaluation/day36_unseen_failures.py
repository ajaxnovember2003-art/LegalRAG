# ============================================================
# LegalRAG - Day 36
# Unseen Query Failure Analysis
# ============================================================

import json
import os


RESULT_PATH = "evaluation/results/unseen_retrieval_results.json"


def normalize_section(section):
    if section is None:
        return None
    return str(section)


def contains_section(results, expected):
    expected = normalize_section(expected)

    for section in results.get("sections", []):
        if normalize_section(section) == expected:
            return True

    return False


def analyze_record(record):

    expected = normalize_section(
        record["expected_section"]
    )

    dense = record["dense"]
    bm25 = record["bm25"]
    rrf = record["rrf"]
    legal = record["legal_reranker"]

    dense_sections = dense["sections"]
    bm25_sections = bm25["sections"]
    rrf_sections = rrf["sections"]
    legal_sections = legal["sections"]

    # --------------------------------------------------------
    # Candidate availability
    # --------------------------------------------------------

    dense_has = contains_section(
        dense,
        expected
    )

    bm25_has = contains_section(
        bm25,
        expected
    )

    rrf_has = contains_section(
        rrf,
        expected
    )

    legal_has = contains_section(
        legal,
        expected
    )

    # --------------------------------------------------------
    # Determine bottleneck
    # --------------------------------------------------------

    if expected in legal_sections[:1]:
        bottleneck = "NO_FAILURE"

    elif rrf_has:
        bottleneck = "RERANKER_FAILURE"

    elif dense_has or bm25_has:
        bottleneck = "RRF_FAILURE"

    else:
        bottleneck = "CANDIDATE_GENERATION_FAILURE"

    return {
        "id": record["id"],
        "query": record["query"],
        "expected_section": expected,

        "dense_top5": dense_sections,
        "bm25_top5": bm25_sections,
        "rrf_top5": rrf_sections,
        "legal_reranker_top5": legal_sections,

        "dense_contains_expected": dense_has,
        "bm25_contains_expected": bm25_has,
        "rrf_contains_expected": rrf_has,
        "legal_contains_expected": legal_has,

        "bottleneck": bottleneck
    }


def main():

    print("=" * 80)
    print("LegalRAG Day 36 - Unseen Query Failure Analysis")
    print("=" * 80)

    if not os.path.exists(RESULT_PATH):
        print()
        print("ERROR: Results file not found:")
        print(RESULT_PATH)
        return

    with open(
        RESULT_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        records = json.load(f)

    analyses = []

    for record in records:

        analysis = analyze_record(record)

        # Only show failures
        if analysis["legal_reranker_top5"][0] != analysis["expected_section"]:
            analyses.append(analysis)

    # --------------------------------------------------------
    # Print failures
    # --------------------------------------------------------

    print()
    print(f"Total queries: {len(records)}")
    print(f"R@1 failures: {len(analyses)}")
    print()

    for item in analyses:

        print("-" * 80)

        print(
            f"Query {item['id']}"
        )

        print(
            f"Expected: {item['expected_section']}"
        )

        print(
            f"Query: {item['query']}"
        )

        print()

        print(
            f"Dense Top-5 : {item['dense_top5']}"
        )

        print(
            f"BM25 Top-5  : {item['bm25_top5']}"
        )

        print(
            f"RRF Top-5   : {item['rrf_top5']}"
        )

        print(
            f"Legal Top-5 : {item['legal_reranker_top5']}"
        )

        print()

        print(
            "Expected in Dense:",
            item["dense_contains_expected"]
        )

        print(
            "Expected in BM25 :",
            item["bm25_contains_expected"]
        )

        print(
            "Expected in RRF  :",
            item["rrf_contains_expected"]
        )

        print(
            "Expected in Legal:",
            item["legal_contains_expected"]
        )

        print(
            f"Bottleneck: {item['bottleneck']}"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    counts = {}

    for item in analyses:

        bottleneck = item["bottleneck"]

        counts[bottleneck] = (
            counts.get(bottleneck, 0) + 1
        )

    print()
    print("=" * 80)
    print("FAILURE SUMMARY")
    print("=" * 80)

    for bottleneck, count in counts.items():

        print(
            f"{bottleneck}: {count}"
        )

    # --------------------------------------------------------
    # Save analysis
    # --------------------------------------------------------

    output_path = (
        "evaluation/results/"
        "day36_unseen_failure_analysis.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analyses,
            f,
            indent=2
        )

    print()
    print("=" * 80)
    print("Analysis saved:")
    print(output_path)
    print("=" * 80)


if __name__ == "__main__":
    main()