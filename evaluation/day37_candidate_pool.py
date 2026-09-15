import json
from pathlib import Path


RESULTS_PATH = Path("evaluation/results/unseen_retrieval_results.json")
OUTPUT_PATH = Path("evaluation/results/day37_candidate_pool_analysis.json")


def main():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)

    target_ids = {15, 16}

    print("=" * 80)
    print("LegalRAG Day 37 - Deep Candidate Pool Analysis")
    print("=" * 80)

    analysis = []

    for record in results:
        query_id = record["id"]

        if query_id not in target_ids:
            continue

        expected = str(record["expected_section"])

        dense = record["dense"]
        bm25 = record["bm25"]

        dense_candidates = [
            str(section)
            for section in dense.get("candidate_sections", [])
        ]

        bm25_candidates = [
            str(section)
            for section in bm25.get("candidate_sections", [])
        ]

        dense_rank = (
            dense_candidates.index(expected) + 1
            if expected in dense_candidates
            else None
        )

        bm25_rank = (
            bm25_candidates.index(expected) + 1
            if expected in bm25_candidates
            else None
        )

        print("-" * 80)
        print(f"Query {query_id}")
        print(f"Expected section: {expected}")
        print(f"Query: {record['query']}")
        print()

        print(f"Dense candidate count : {len(dense_candidates)}")
        print(f"BM25 candidate count  : {len(bm25_candidates)}")
        print()

        print(f"§{expected} Dense candidate rank: {dense_rank}")
        print(f"§{expected} BM25 candidate rank : {bm25_rank}")
        print()

        print("Dense Top-10:")
        print(dense_candidates[:10])

        print()
        print("BM25 Top-10:")
        print(bm25_candidates[:10])

        print()
        print(f"§{expected} in Dense candidates: {expected in dense_candidates}")
        print(f"§{expected} in BM25 candidates : {expected in bm25_candidates}")

        if expected in dense_candidates or expected in bm25_candidates:
            bottleneck = "RANKING_OR_RERANKING"
        else:
            bottleneck = "CANDIDATE_GENERATION"

        print(f"Bottleneck: {bottleneck}")

        analysis.append({
            "id": query_id,
            "query": record["query"],
            "expected_section": expected,
            "dense_candidate_count": len(dense_candidates),
            "bm25_candidate_count": len(bm25_candidates),
            "dense_expected_rank": dense_rank,
            "bm25_expected_rank": bm25_rank,
            "dense_contains_expected": expected in dense_candidates,
            "bm25_contains_expected": expected in bm25_candidates,
            "bottleneck": bottleneck,
            "dense_candidates": dense_candidates,
            "bm25_candidates": bm25_candidates,
        })

    print()
    print("=" * 80)
    print("DAY 37 SUMMARY")
    print("=" * 80)

    candidate_generation_failures = sum(
        1 for item in analysis
        if item["bottleneck"] == "CANDIDATE_GENERATION"
    )

    ranking_cases = sum(
        1 for item in analysis
        if item["bottleneck"] == "RANKING_OR_RERANKING"
    )

    print(f"Queries analyzed: {len(analysis)}")
    print(f"Candidate-generation failures: {candidate_generation_failures}")
    print(f"Ranking/reranking cases: {ranking_cases}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print()
    print("Analysis saved:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()