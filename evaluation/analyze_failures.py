import json


RESULT_PATH = (
    "evaluation/results/"
    "hard_retrieval_results.json"
)


def get_rank(result, expected_section):
    if expected_section is None:
        return None

    expected_section = str(
        expected_section
    ).strip()

    sections = result.get(
        "sections",
        []
    )

    for rank, section in enumerate(
        sections,
        start=1
    ):
        if str(section).strip() == expected_section:
            return rank

    return None


def candidate_rank(
    result,
    expected_section
):
    if expected_section is None:
        return None

    return result.get(
        "expected_candidate_rank"
    )


def section_in_top_k(
    result,
    expected_section,
    k=5
):
    rank = get_rank(
        result,
        expected_section
    )

    return (
        rank is not None
        and rank <= k
    )


def classify_failure(
    query_result
):
    expected = query_result.get(
        "expected_section"
    )

    dense = query_result.get(
        "dense",
        {}
    )

    bm25 = query_result.get(
        "bm25",
        {}
    )

    rrf = query_result.get(
        "rrf",
        {}
    )

    legal = query_result.get(
        "legal_reranker",
        {}
    )

    strict = query_result.get(
        "legal_reranker_strict",
        {}
    )

    legal_success = section_in_top_k(
        legal,
        expected,
        5
    )

    strict_success = section_in_top_k(
        strict,
        expected,
        5
    )

    # --------------------------------------------------
    # 1. Final LegalRAG retrieval success
    # --------------------------------------------------

    if legal_success:
        if not strict_success:
            return (
                "section_prior_recovery"
            )

        return (
            "retrieval_success"
        )

    # --------------------------------------------------
    # 2. Candidate-generation analysis
    # --------------------------------------------------

    dense_candidate_rank = candidate_rank(
        dense,
        expected
    )

    bm25_candidate_rank = candidate_rank(
        bm25,
        expected
    )

    rrf_candidate_rank = candidate_rank(
        rrf,
        expected
    )

    # Expected section never entered ANY
    # candidate pool.
    if (
        dense_candidate_rank is None
        and bm25_candidate_rank is None
        and rrf_candidate_rank is None
    ):
        return (
            "candidate_generation_failure"
        )

    # --------------------------------------------------
    # 3. Section reached reranker but was lost
    # --------------------------------------------------

    return (
        "reranker_failure"
    )


def main():

    with open(
        RESULT_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        results = json.load(f)

    categories = {}

    failures = []

    for index, query_result in enumerate(
        results,
        start=1
    ):
        category = classify_failure(
            query_result
        )

        categories[category] = (
            categories.get(category, 0)
            + 1
        )

        if category != "retrieval_success":
            failures.append(
                (
                    index,
                    query_result,
                    category
                )
            )

    print(
        "\n"
        "FAILURE CATEGORY SUMMARY"
    )

    for category, count in sorted(
        categories.items()
    ):
        print(
            f"{category:<35}"
            f"{count}"
        )

    print(
        "\n"
        "DETAILED FAILURES"
    )

    for (
        index,
        query_result,
        category
    ) in failures:

        expected = query_result.get(
            "expected_section"
        )

        query = query_result.get(
            "query",
            ""
        )

        dense_rank = candidate_rank(
            query_result.get(
                "dense",
                {}
            ),
            expected
        )

        bm25_rank = candidate_rank(
            query_result.get(
                "bm25",
                {}
            ),
            expected
        )

        rrf_rank = candidate_rank(
            query_result.get(
                "rrf",
                {}
            ),
            expected
        )

        legal_rank = get_rank(
            query_result.get(
                "legal_reranker",
                {}
            ),
            expected
        )

        strict_rank = get_rank(
            query_result.get(
                "legal_reranker_strict",
                {}
            ),
            expected
        )

        print(
            "\n"
            f"Q{index}: "
            f"{category}"
        )

        print(
            f"Query: {query}"
        )

        print(
            f"Expected section: "
            f"{expected}"
        )

        print(
            f"Dense candidate rank: "
            f"{dense_rank}"
        )

        print(
            f"BM25 candidate rank: "
            f"{bm25_rank}"
        )

        print(
            f"RRF candidate rank: "
            f"{rrf_rank}"
        )

        print(
            f"LegalRAG rank: "
            f"{legal_rank}"
        )

        print(
            f"Strict LegalRAG rank: "
            f"{strict_rank}"
        )


if __name__ == "__main__":
    main()