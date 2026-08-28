import json
import os

from backend.app.services.retrieval import (
    retrieve_dense
)

from backend.app.services.bm25 import (
    search_bm25
)

from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    rerank_results
)


# ============================================================
# CONFIG
# ============================================================

DATASET_PATH = (
    "evaluation/dataset/legal_queries.json"
)

RESULT_PATH = (
    "evaluation/results/retrieval_results.json"
)

TOP_K = 5


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
# SECTION IN TOP K
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

    return (
        correct_section
        in sections
    )


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
# LOAD DATASET
# ============================================================

def load_dataset():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# PRINT PIPELINE
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
# EVALUATE
# ============================================================

def evaluate():

    queries = load_dataset()

    evaluation_results = []

    for item in queries:

        query = item[
            "query"
        ]

        correct_section = item.get(
            "correct_section"
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
            k=10
        )

        # ====================================================
        # BM25
        # ====================================================

        print(
            "\nRunning BM25 Retrieval..."
        )

        bm25_results = search_bm25(
            query,
            k=10
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
        # RERANK
        # ====================================================

        print(
            "\nApplying LegalRAG reranker..."
        )

        reranked_results = rerank_results(
            query,
            rrf_results,
            top_k=10
        )

        # ====================================================
        # METRICS
        # ====================================================

        result = {

            "id": item["id"],

            "query": query,

            "expected_section":
                correct_section,

            "dense": {

                "sections": [
                    get_section(x)
                    for x in dense_results[:TOP_K]
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
                    ),
            },

            "bm25": {

                "sections": [
                    get_section(x)
                    for x in bm25_results[:TOP_K]
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
                    ),
            },

            "rrf": {

                "sections": [
                    get_section(x)
                    for x in rrf_results[:TOP_K]
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
                    ),
            },

            "legal_reranker": {

                "sections": [
                    get_section(x)
                    for x in reranked_results[:TOP_K]
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
                    ),
            }
        }

        evaluation_results.append(
            result
        )

        # ====================================================
        # PRINT
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
    # SAVE
    # ========================================================

    os.makedirs(
        os.path.dirname(
            RESULT_PATH
        ),
        exist_ok=True
    )

    with open(
        RESULT_PATH,
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
    # OVERALL METRICS
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

    for system in systems:

        valid_results = [
            r
            for r in evaluation_results
            if r["expected_section"]
            is not None
        ]

        if not valid_results:

            continue

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

        print(
            f"\n{system.upper()}"
        )

        print(
            f"Recall@1 : "
            f"{recall1:.4f}"
        )

        print(
            f"Recall@3 : "
            f"{recall3:.4f}"
        )

        print(
            f"Recall@5 : "
            f"{recall5:.4f}"
        )

        print(
            f"MRR      : "
            f"{mrr:.4f}"
        )

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
        f"Results saved to: "
        f"{RESULT_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluate()