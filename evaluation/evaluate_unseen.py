# ============================================================
# LegalRAG - Day 35
# Held-Out Unseen Query Generalization Evaluation
# ============================================================

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from backend.app.services.retrieval import retrieve_dense
from backend.app.services.bm25 import search_bm25
from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    rerank_results
)


DATASET_PATH = "evaluation/dataset/unseen_queries.json"
RESULT_DIR = "evaluation/results"


TOP_K = 5
CANDIDATE_K = 50


def get_section(result):
    """
    Extract section number from a retrieval result.
    Supports the result formats currently used by LegalRAG.
    """

    if not result:
        return None

    if isinstance(result, dict):

        for key in [
            "section",
            "section_number",
            "section_id"
        ]:
            if key in result and result[key] is not None:
                return str(result[key])

        metadata = result.get("metadata")

        if isinstance(metadata, dict):

            for key in [
                "section",
                "section_number",
                "section_id"
            ]:
                if key in metadata and metadata[key] is not None:
                    return str(metadata[key])

    return None


def section_in_results(results, expected_section, k):
    """
    Check whether the expected section appears in top-k results.
    """

    expected_section = str(expected_section)

    for result in results[:k]:

        section = get_section(result)

        if section == expected_section:
            return True

    return False


def reciprocal_rank(results, expected_section):
    """
    Calculate reciprocal rank of the expected section.
    """

    expected_section = str(expected_section)

    for rank, result in enumerate(results, start=1):

        if get_section(result) == expected_section:
            return 1.0 / rank

    return 0.0


def evaluate_method(results, expected_section):

    return {
        "sections": [
            get_section(r)
            for r in results[:TOP_K]
        ],
        "recall_at_1": section_in_results(
            results,
            expected_section,
            1
        ),
        "recall_at_3": section_in_results(
            results,
            expected_section,
            3
        ),
        "recall_at_5": section_in_results(
            results,
            expected_section,
            5
        ),
        "reciprocal_rank": reciprocal_rank(
            results,
            expected_section
        )
    }


def average_metric(records, metric):

    if not records:
        return 0.0

    return sum(
        1.0 if r[metric] else 0.0
        for r in records
    ) / len(records)


def mean_mrr(records):

    if not records:
        return 0.0

    return sum(
        r["reciprocal_rank"]
        for r in records
    ) / len(records)


def load_dataset():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def main():

    print("=" * 80)
    print("LegalRAG Day 35 - Unseen Query Generalization Evaluation")
    print("=" * 80)

    queries = load_dataset()

    print(f"Total unseen queries: {len(queries)}")
    print(f"Candidate depth: {CANDIDATE_K}")
    print(f"Final top-k: {TOP_K}")
    print()

    all_results = []

    for item in queries:

        query_id = item["id"]
        query = item["query"]
        expected_section = str(
            item["expected_section"]
        )

        print("-" * 80)
        print(f"Query {query_id}")
        print(f"Query: {query}")
        print(f"Expected section: {expected_section}")

        # ----------------------------------------------------
        # Dense Retrieval
        # ----------------------------------------------------

        dense_results = retrieve_dense(
            query,
            k=CANDIDATE_K
        )

        # ----------------------------------------------------
        # BM25 Retrieval
        # ----------------------------------------------------

        bm25_results = search_bm25(
            query,
            k=CANDIDATE_K
        )

        # ----------------------------------------------------
        # RRF
        # ----------------------------------------------------

        rrf_results = reciprocal_rank_fusion(
            dense_results,
            bm25_results
        )

        # ----------------------------------------------------
        # LegalRAG Reranker
        # ----------------------------------------------------

        legal_results = rerank_results(
            query,
            rrf_results,
            top_k=TOP_K
        )

        # ----------------------------------------------------
        # Evaluate
        # ----------------------------------------------------

        dense_eval = evaluate_method(
            dense_results,
            expected_section
        )

        bm25_eval = evaluate_method(
            bm25_results,
            expected_section
        )

        rrf_eval = evaluate_method(
            rrf_results,
            expected_section
        )

        legal_eval = evaluate_method(
            legal_results,
            expected_section
        )

        print(
            f"Dense  : {dense_eval['sections']}"
        )

        print(
            f"BM25   : {bm25_eval['sections']}"
        )

        print(
            f"RRF    : {rrf_eval['sections']}"
        )

        print(
            f"LegalRAG: {legal_eval['sections']}"
        )

        all_results.append({
            "id": query_id,
            "query": query,
            "expected_section": expected_section,

            "dense": dense_eval,
            "bm25": bm25_eval,
            "rrf": rrf_eval,
            "legal_reranker": legal_eval
        })

    # ========================================================
    # Summary
    # ========================================================

    summary = {}

    for method in [
        "dense",
        "bm25",
        "rrf",
        "legal_reranker"
    ]:

        records = [
            r[method]
            for r in all_results
        ]

        summary[method] = {
            "recall_at_1": average_metric(
                records,
                "recall_at_1"
            ),
            "recall_at_3": average_metric(
                records,
                "recall_at_3"
            ),
            "recall_at_5": average_metric(
                records,
                "recall_at_5"
            ),
            "mrr": mean_mrr(records)
        }

    # ========================================================
    # Save Results
    # ========================================================

    os.makedirs(
        RESULT_DIR,
        exist_ok=True
    )

    results_path = os.path.join(
        RESULT_DIR,
        "unseen_retrieval_results.json"
    )

    summary_path = os.path.join(
        RESULT_DIR,
        "unseen_retrieval_summary.json"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_results,
            f,
            indent=2
        )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=2
        )

    # ========================================================
    # Print Summary
    # ========================================================

    print()
    print("=" * 80)
    print("UNSEEN QUERY RESULTS")
    print("=" * 80)

    for method, metrics in summary.items():

        print()
        print(method.upper())

        print(
            f"  Recall@1: "
            f"{metrics['recall_at_1']:.4f}"
        )

        print(
            f"  Recall@3: "
            f"{metrics['recall_at_3']:.4f}"
        )

        print(
            f"  Recall@5: "
            f"{metrics['recall_at_5']:.4f}"
        )

        print(
            f"  MRR     : "
            f"{metrics['mrr']:.4f}"
        )

    print()
    print("=" * 80)
    print("Results saved:")
    print(results_path)
    print(summary_path)
    print("=" * 80)


if __name__ == "__main__":
    main()
