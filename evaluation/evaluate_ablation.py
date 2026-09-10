import json
import os
import sys


# ============================================================
# WINDOWS / PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# LEGALRAG IMPORTS
# ============================================================

from backend.app.services.retrieval import (
    retrieve_dense
)

from backend.app.services.bm25 import (
    search_bm25
)

from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    calculate_legal_score
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = (
    "evaluation/dataset/legal_queries.json"
)

RESULT_PATH = (
    "evaluation/results/ablation_results.json"
)

DENSE_K = 10
BM25_K = 10
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
            == correct_section
        ):

            return 1.0 / rank

    return 0.0


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    results,
    correct_section
):

    if correct_section is None:

        return {
            "recall_at_1": None,
            "recall_at_3": None,
            "recall_at_5": None,
            "reciprocal_rank": None
        }

    return {

        "recall_at_1":
            section_in_results(
                results,
                correct_section,
                1
            ),

        "recall_at_3":
            section_in_results(
                results,
                correct_section,
                3
            ),

        "recall_at_5":
            section_in_results(
                results,
                correct_section,
                5
            ),

        "reciprocal_rank":
            reciprocal_rank(
                results,
                correct_section
            )
    }


# ============================================================
# ABLATION SCORE
# ============================================================

def calculate_ablation_score(
    query,
    result,
    use_lexical=True,
    use_concept=True,
    use_punishment=True,
    use_section=True
):

    text = result.get(
        "text",
        ""
    )

    metadata = result.get(
        "metadata",
        {}
    )

    # Import the individual scoring functions.
    from backend.app.services.hybrid_retrieval import (
        lexical_similarity,
        concept_score,
        punishment_score,
        section_score,
        detect_offence
    )

    offence = detect_offence(
        query
    )

    lexical = (
        lexical_similarity(
            query,
            text
        )
        if use_lexical
        else 0.0
    )

    concept = (
        concept_score(
            offence,
            text
        )
        if use_concept
        else 0.0
    )

    punishment = (
        punishment_score(
            query,
            text
        )
        if use_punishment
        else 0.0
    )

    section = (
        section_score(
            offence,
            metadata
        )
        if use_section
        else 0.0
    )

    base_score = float(
        result.get(
            "score",
            0.0
        )
    )

    legal_boost = (

        section * 0.35

        +

        concept * 0.20

        +

        lexical * 0.10

        +

        punishment * 0.10
    )

    return (
        base_score
        +
        legal_boost
    )


# ============================================================
# APPLY ABLATION
# ============================================================

def apply_ablation(
    query,
    results,
    use_lexical=True,
    use_concept=True,
    use_punishment=True,
    use_section=True
):

    reranked = []

    for result in results:

        item = result.copy()

        item["ablation_score"] = (
            calculate_ablation_score(
                query,
                item,
                use_lexical=use_lexical,
                use_concept=use_concept,
                use_punishment=use_punishment,
                use_section=use_section
            )
        )

        reranked.append(
            item
        )

    reranked.sort(
        key=lambda x:
        x["ablation_score"],
        reverse=True
    )

    # Keep one result per legal section.
    final = []

    seen_sections = set()

    for result in reranked:

        section = get_section(
            result
        )

        if section in seen_sections:
            continue

        seen_sections.add(
            section
        )

        final.append(
            result
        )

        if len(final) >= TOP_K:
            break

    return final


# ============================================================
# ABLATION CONFIGURATIONS
# ============================================================

ABLATIONS = {

    "dense_only": {
        "description":
            "Dense retrieval only"
    },

    "rrf_baseline": {
        "description":
            "Dense + BM25 + RRF"
    },

    "rrf_plus_lexical": {
        "description":
            "RRF + lexical similarity",
        "use_lexical": True,
        "use_concept": False,
        "use_punishment": False,
        "use_section": False
    },

    "rrf_plus_concept": {
        "description":
            "RRF + legal concept score",
        "use_lexical": False,
        "use_concept": True,
        "use_punishment": False,
        "use_section": False
    },

    "rrf_plus_punishment": {
        "description":
            "RRF + punishment intent score",
        "use_lexical": False,
        "use_concept": False,
        "use_punishment": True,
        "use_section": False
    },

    "rrf_plus_section": {
        "description":
            "RRF + section matching",
        "use_lexical": False,
        "use_concept": False,
        "use_punishment": False,
        "use_section": True
    },

    "rrf_lexical_concept": {
        "description":
            "RRF + lexical + concept",
        "use_lexical": True,
        "use_concept": True,
        "use_punishment": False,
        "use_section": False
    },

    "rrf_lexical_concept_punishment": {
        "description":
            "RRF + lexical + concept + punishment",
        "use_lexical": True,
        "use_concept": True,
        "use_punishment": True,
        "use_section": False
    },

    "full_legalrag": {
        "description":
            "Full LegalRAG reranker",
        "use_lexical": True,
        "use_concept": True,
        "use_punishment": True,
        "use_section": True
    }
}


# ============================================================
# EVALUATE ONE SYSTEM
# ============================================================

def evaluate_system(
    system_name,
    queries,
    retrieval_cache
):

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"ABLATION: {system_name}"
    )

    print(
        ABLATIONS[
            system_name
        ]["description"]
    )

    print(
        "=" * 70
    )

    results = []

    config = ABLATIONS[
        system_name
    ]

    for item in queries:

        query = item[
            "query"
        ]

        correct_section = item.get(
            "correct_section"
        )

        dense_results = retrieval_cache[
            item["id"]
        ]["dense"]

        rrf_results = retrieval_cache[
            item["id"]
        ]["rrf"]

        # ----------------------------------------------------
        # DENSE ONLY
        # ----------------------------------------------------

        if system_name == "dense_only":

            final_results = (
                dense_results[
                    :TOP_K
                ]
            )

        # ----------------------------------------------------
        # RRF BASELINE
        # ----------------------------------------------------

        elif system_name == "rrf_baseline":

            final_results = (
                rrf_results[
                    :TOP_K
                ]
            )

        # ----------------------------------------------------
        # LEGAL ABLATIONS
        # ----------------------------------------------------

        else:

            final_results = apply_ablation(
                query,
                rrf_results,
                use_lexical=config.get(
                    "use_lexical",
                    False
                ),
                use_concept=config.get(
                    "use_concept",
                    False
                ),
                use_punishment=config.get(
                    "use_punishment",
                    False
                ),
                use_section=config.get(
                    "use_section",
                    False
                )
            )

        metrics = calculate_metrics(
            final_results,
            correct_section
        )

        results.append({

            "id":
                item["id"],

            "query":
                query,

            "expected_section":
                correct_section,

            "sections": [
                get_section(x)
                for x in final_results
            ],

            **metrics
        })

    return results


# ============================================================
# OVERALL METRICS
# ============================================================

def overall_metrics(
    results
):

    valid = [
        r
        for r in results
        if r[
            "expected_section"
        ] is not None
    ]

    if not valid:

        return {}

    recall1 = sum(
        bool(
            r["recall_at_1"]
        )
        for r in valid
    ) / len(valid)

    recall3 = sum(
        bool(
            r["recall_at_3"]
        )
        for r in valid
    ) / len(valid)

    recall5 = sum(
        bool(
            r["recall_at_5"]
        )
        for r in valid
    ) / len(valid)

    mrr = sum(
        r["reciprocal_rank"]
        for r in valid
    ) / len(valid)

    return {

        "recall_at_1":
            recall1,

        "recall_at_3":
            recall3,

        "recall_at_5":
            recall5,

        "mrr":
            mrr,

        "evaluated_queries":
            len(valid)
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

def evaluate():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "LEGALRAG ABLATION STUDY"
    )

    print(
        "=" * 70
    )

    queries = load_dataset()

    retrieval_cache = {}

    # ========================================================
    # RETRIEVE ONCE
    # ========================================================

    print(
        "\nPreparing retrieval cache..."
    )

    for item in queries:

        query = item[
            "query"
        ]

        print(
            f"\nQuery {item['id']}: "
            f"{query}"
        )

        dense_results = retrieve_dense(
            query,
            k=DENSE_K
        )

        bm25_results = search_bm25(
            query,
            k=BM25_K
        )

        rrf_results = (
            reciprocal_rank_fusion(
                dense_results,
                bm25_results
            )
        )

        retrieval_cache[
            item["id"]
        ] = {

            "dense":
                dense_results,

            "bm25":
                bm25_results,

            "rrf":
                rrf_results
        }

    # ========================================================
    # RUN ABLATIONS
    # ========================================================

    all_results = {}

    for system_name in ABLATIONS:

        system_results = evaluate_system(
            system_name,
            queries,
            retrieval_cache
        )

        all_results[
            system_name
        ] = {

            "description":
                ABLATIONS[
                    system_name
                ]["description"],

            "queries":
                system_results,

            "overall":
                overall_metrics(
                    system_results
                )
        }

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
            all_results,
            f,
            indent=4,
            ensure_ascii=False
        )

    # ========================================================
    # FINAL TABLE
    # ========================================================

    print(
        "\n\n"
        + "=" * 70
    )

    print(
        "ABLATION STUDY RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"{'SYSTEM':<38}"
        f"{'R@1':>8}"
        f"{'R@3':>8}"
        f"{'R@5':>8}"
        f"{'MRR':>8}"
    )

    print(
        "-" * 70
    )

    for system_name, data in (
        all_results.items()
    ):

        metrics = data[
            "overall"
        ]

        print(
            f"{system_name:<38}"
            f"{metrics.get('recall_at_1', 0):>8.4f}"
            f"{metrics.get('recall_at_3', 0):>8.4f}"
            f"{metrics.get('recall_at_5', 0):>8.4f}"
            f"{metrics.get('mrr', 0):>8.4f}"
        )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "ABLATION EVALUATION COMPLETE"
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