import json
import os
import sys

from backend.app.services.retrieval import retrieve_dense
from backend.app.services.bm25 import search_bm25
from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    rerank_results
)


# ============================================================
# CONFIG
# ============================================================

NORMAL_DATASET_PATH = (
    "evaluation/dataset/legal_queries.json"
)

RESULT_DIR = (
    "evaluation/results"
)

TOP_K = 5

CANDIDATE_K = 10

# ============================================================
# GET SECTION
# ============================================================

def get_section(result):

    metadata = result.get(
        "metadata",
        {}
    )

    return str(
        metadata.get(
            "section",
            ""
        )
    ).strip()


# ============================================================
# SECTION IN RESULTS
# ============================================================

def section_in_results(
    results,
    correct_section,
    k
):

    if correct_section is None:
        return None

    correct_section = str(
        correct_section
    ).strip()

    sections = [
        get_section(result)
        for result in results[:k]
    ]

    return correct_section in sections


# ============================================================
# RECIPROCAL RANK
# ============================================================

def reciprocal_rank(
    results,
    correct_section
):

    if correct_section is None:
        return None

    correct_section = str(
        correct_section
    ).strip()

    for rank, result in enumerate(
        results,
        start=1
    ):

        if (
            get_section(result)
            ==
            correct_section
        ):

            return 1 / rank

    return 0.0


# ============================================================
# LOAD NORMAL DATASET
# ============================================================

def load_normal_dataset():

    with open(
        NORMAL_DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    # Normalize field names
    normalized = []

    for index, item in enumerate(
        data,
        start=1
    ):

        normalized.append({
            "id": item.get(
                "id",
                index
            ),

            "query": item[
                "query"
            ],

            "expected_section":
                item.get(
                    "correct_section",
                    item.get(
                        "expected_section"
                    )
                )
        })

    return normalized


# ============================================================
# LOAD DAY-27 HARD DATASET
# ============================================================

def load_hard_dataset():

    from evaluation.test_queries_hard import HARD_QUERIES

    normalized = []

    for index, item in enumerate(
        HARD_QUERIES,
        start=1
    ):
        normalized.append({
            "id": index,
            "query": item["query"],
            "expected_section": item.get("expected_section")
        })

    return normalized


# ============================================================
# SELECT DATASET
# ============================================================

def load_dataset(mode):

    if mode == "hard":

        print(
            "\nLoading Day-27 HARD benchmark..."
        )

        return load_hard_dataset()

    print(
        "\nLoading NORMAL benchmark..."
    )

    return load_normal_dataset()


# ============================================================
# PRINT PIPELINE RESULTS
# ============================================================

def print_pipeline_results(
    name,
    results
):

    sections = [
        get_section(x)
        for x in results[:TOP_K]
    ]

    print(
        f"{name}:"
    )

    print(
        sections
    )


# ============================================================
# CALCULATE OVERALL METRICS
# ============================================================

def calculate_metrics(
    evaluation_results,
    system
):

    valid_results = [
        r
        for r in evaluation_results
        if r[
            "expected_section"
        ] is not None
    ]

    if not valid_results:

        return {
            "recall_at_1": 0.0,
            "recall_at_3": 0.0,
            "recall_at_5": 0.0,
            "mrr": 0.0
        }

    recall1 = sum(
        bool(
            r[system][
                "recall_at_1"
            ]
        )
        for r in valid_results
    ) / len(valid_results)

    recall3 = sum(
        bool(
            r[system][
                "recall_at_3"
            ]
        )
        for r in valid_results
    ) / len(valid_results)

    recall5 = sum(
        bool(
            r[system][
                "recall_at_5"
            ]
        )
        for r in valid_results
    ) / len(valid_results)

    mrr = sum(
        r[system][
            "reciprocal_rank"
        ]
        for r in valid_results
    ) / len(valid_results)

    return {
        "recall_at_1": recall1,
        "recall_at_3": recall3,
        "recall_at_5": recall5,
        "mrr": mrr
    }


# ============================================================
# EVALUATE
# ============================================================

def evaluate(
    mode="normal",
    candidate_k=10
    ):

    queries = load_dataset(
        mode
    )
    
    evaluation_results = []
    
    print()
    
    print("=" * 70)
    
    print(f"Candidate Generation Depth: {candidate_k}")
    
    print(f"Final Reranker Top-K: 10")
    
    print("=" * 70)

    for item in queries:
        if item.get("id") not in [15, 16]:
            continue

        query = item[
            "query"
        ]

        correct_section = item.get(
            "expected_section"
        )

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"Query {item['id']}: "
            f"{query}"
        )

        print(
            f"Expected Section: "
            f"{correct_section}"
        )

        print(
            "=" * 70
        )

        # ====================================================
        # DENSE
        # ====================================================

        print(
            "\nRunning Dense Retrieval..."
        )

        dense_results = retrieve_dense(
            query,
            k=candidate_k
        )

        # ====================================================
        # BM25
        # ====================================================

        print(
            "\nRunning BM25 Retrieval..."
        )

        bm25_results = search_bm25(
            query,
            k=candidate_k
        )

        # ====================================================
        # RRF
        # ====================================================

        print(
            "\nApplying RRF..."
        )

        rrf_results = reciprocal_rank_fusion(
            dense_results,
            bm25_results
        )

        # ====================================================
        # LEGAL RERANKER
        # ====================================================

        print(
            "\nApplying LegalRAG reranker..."
        )

        reranked_results = rerank_results(
            query,
            rrf_results,
            top_k=candidate_k
        )

        # ====================================================
        # STORE RESULTS
        # ====================================================

        result = {

            "id":
                item["id"],

            "query":
                query,

            "expected_section":
                correct_section,

            "dense": {

                "sections": [
                    get_section(x)
                    for x in dense_results[
                        :TOP_K
                    ]
                ],

                "recall_at_1":
                    section_in_results(
                        dense_results,
                        correct_section,
                        1
                    ),

                "recall_at_3":
                    section_in_results(
                        dense_results,
                        correct_section,
                        3
                    ),

                "recall_at_5":
                    section_in_results(
                        dense_results,
                        correct_section,
                        5
                    ),

                "reciprocal_rank":
                    reciprocal_rank(
                        dense_results,
                        correct_section
                    )
            },

            "bm25": {

                "sections": [
                    get_section(x)
                    for x in bm25_results[
                        :TOP_K
                    ]
                ],

                "recall_at_1":
                    section_in_results(
                        bm25_results,
                        correct_section,
                        1
                    ),

                "recall_at_3":
                    section_in_results(
                        bm25_results,
                        correct_section,
                        3
                    ),

                "recall_at_5":
                    section_in_results(
                        bm25_results,
                        correct_section,
                        5
                    ),

                "reciprocal_rank":
                    reciprocal_rank(
                        bm25_results,
                        correct_section
                    )
            },

            "rrf": {

                "sections": [
                    get_section(x)
                    for x in rrf_results[
                        :TOP_K
                    ]
                ],

                "recall_at_1":
                    section_in_results(
                        rrf_results,
                        correct_section,
                        1
                    ),

                "recall_at_3":
                    section_in_results(
                        rrf_results,
                        correct_section,
                        3
                    ),

                "recall_at_5":
                    section_in_results(
                        rrf_results,
                        correct_section,
                        5
                    ),

                "reciprocal_rank":
                    reciprocal_rank(
                        rrf_results,
                        correct_section
                    )
            },

            "legal_reranker": {

                "sections": [
                    get_section(x)
                    for x in reranked_results[
                        :TOP_K
                    ]
                ],

                "recall_at_1":
                    section_in_results(
                        reranked_results,
                        correct_section,
                        1
                    ),

                "recall_at_3":
                    section_in_results(
                        reranked_results,
                        correct_section,
                        3
                    ),

                "recall_at_5":
                    section_in_results(
                        reranked_results,
                        correct_section,
                        5
                    ),

                "reciprocal_rank":
                    reciprocal_rank(
                        reranked_results,
                        correct_section
                    )
            }
        }

        evaluation_results.append(
            result
        )

        # ====================================================
        # PRINT TOP RESULTS
        # ====================================================

        print()

        print_pipeline_results(
            "Dense Top-5",
            dense_results
        )

        print_pipeline_results(
            "BM25 Top-5",
            bm25_results
        )

        print_pipeline_results(
            "RRF Top-5",
            rrf_results
        )

        print_pipeline_results(
            "LegalRAG Reranker Top-5",
            reranked_results
        )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    os.makedirs(
        RESULT_DIR,
        exist_ok=True
    )

    if mode == "hard":

        result_path = (
            f"{RESULT_DIR}/"
            "hard_retrieval_results.json"
        )

    else:

        result_path = (
            f"{RESULT_DIR}/"
            "retrieval_results.json"
        )

    with open(
        result_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            evaluation_results,
            f,
            indent=4,
            ensure_ascii=False
        )

    # ========================================================
    # OVERALL PERFORMANCE
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "OVERALL RETRIEVAL PERFORMANCE"
    )

    print(
        "=" * 70
    )

    systems = [
        "dense",
        "bm25",
        "rrf",
        "legal_reranker"
    ]

    overall_metrics = {}

    for system in systems:

        metrics = calculate_metrics(
            evaluation_results,
            system
        )

        overall_metrics[
            system
        ] = metrics

        print(
            f"\n{system.upper()}"
        )

        print(
            f"Recall@1 : "
            f"{metrics['recall_at_1']:.4f}"
        )

        print(
            f"Recall@3 : "
            f"{metrics['recall_at_3']:.4f}"
        )

        print(
            f"Recall@5 : "
            f"{metrics['recall_at_5']:.4f}"
        )

        print(
            f"MRR      : "
            f"{metrics['mrr']:.4f}"
        )

    # ========================================================
    # SAVE SUMMARY
    # ========================================================

    summary = {

        "benchmark":
            mode,

        "num_queries":
            len(queries),

        "metrics":
            overall_metrics
    }

    summary_path = (
        f"{RESULT_DIR}/"
        f"{mode}_retrieval_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=4
        )

    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Detailed results: "
        f"{result_path}"
    )

    print(
        f"Summary: "
        f"{summary_path}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    mode = "normal"
    candidate_k = 10

    args = sys.argv[1:]

    i = 0

    while i < len(args):

        argument = args[i].lower()

        if argument in ["hard", "--hard"]:
            mode = "hard"

        elif argument in ["normal", "--normal"]:
            mode = "normal"

        elif argument in ["--k", "-k"]:

            if i + 1 >= len(args):
                print("Error: --k requires a number.")
                sys.exit(1)

            try:
                candidate_k = int(args[i + 1])
            except ValueError:
                print("Error: --k must be an integer.")
                sys.exit(1)

            if candidate_k <= 0:
                print("Error: --k must be greater than 0.")
                sys.exit(1)

            i += 1

        else:
            print("Unknown argument:")
            print(argument)
            print()
            print("Usage:")
            print("  python -m evaluation.evaluate_retrieval")
            print("  python -m evaluation.evaluate_retrieval hard")
            print("  python -m evaluation.evaluate_retrieval hard --k 10")
            print("  python -m evaluation.evaluate_retrieval hard --k 30")
            print("  python -m evaluation.evaluate_retrieval hard --k 50")
            print("  python -m evaluation.evaluate_retrieval hard --k 100")
            sys.exit(1)

        i += 1

    evaluate(
        mode,
        candidate_k=candidate_k
    )