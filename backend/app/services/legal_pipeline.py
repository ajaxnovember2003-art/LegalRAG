# ============================================================
# LEGALRAG END-TO-END PIPELINE
# ============================================================

from backend.app.services.retrieval import (
    multi_query_dense_search,
    generate_retrieval_queries
)

from backend.app.services.bm25 import (
    search_bm25
)

from backend.app.services.hybrid_retrieval import (
    reciprocal_rank_fusion,
    rerank_results
)

from backend.app.services.context_builder import (
    build_legal_context
)

from backend.app.services.llm import (
    generate_answer
)

from backend.app.services.citation import (
    extract_citations,
    verify_answer_grounding
)


# ============================================================
# CONFIGURATION
# ============================================================

DENSE_K = 10
BM25_K = 10
FINAL_K = 5


# ============================================================
# END-TO-END LEGAL QUERY
# ============================================================

def answer_legal_query(query):
    """
    Execute the complete LegalRAG pipeline.

    Pipeline:

        User Query
            ↓
        Query Expansion
            ↓
        Dense Retrieval
            ↓
        BM25 Retrieval
            ↓
        Reciprocal Rank Fusion
            ↓
        LegalRAG Reranking
            ↓
        Context Construction
            ↓
        LLM Generation
            ↓
        Citation Verification
            ↓
        Final Result
    """

    if not query or not query.strip():

        return {
            "query": query,
            "answer": (
                "Please provide a legal question."
            ),
            "sections": [],
            "sources": [],
            "grounded": False,
            "citation_verification": {},
            "retrieval_count": 0
        }

    query = query.strip()

    print("\n")
    print("=" * 70)
    print("LEGALRAG END-TO-END PIPELINE")
    print("=" * 70)

    print(f"\nUSER QUERY:")
    print(query)

    # ========================================================
    # STEP 1 — QUERY EXPANSION
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 1 — QUERY EXPANSION")
    print("-" * 70)

    retrieval_queries = generate_retrieval_queries(
        query
    )

    # ========================================================
    # STEP 2 — DENSE RETRIEVAL
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 2 — DENSE RETRIEVAL")
    print("-" * 70)

    dense_results = multi_query_dense_search(
        retrieval_queries,
        k=DENSE_K
    )

    print(
        f"Dense candidates: "
        f"{len(dense_results)}"
    )

    # ========================================================
    # STEP 3 — BM25 RETRIEVAL
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 3 — BM25 RETRIEVAL")
    print("-" * 70)

    bm25_results = search_bm25(
        query,
        k=BM25_K
    )

    print(
        f"BM25 candidates: "
        f"{len(bm25_results)}"
    )

    # ========================================================
    # STEP 4 — RECIPROCAL RANK FUSION
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 4 — RECIPROCAL RANK FUSION")
    print("-" * 70)

    rrf_results = reciprocal_rank_fusion(
        dense_results,
        bm25_results
    )

    print(
        f"RRF candidates: "
        f"{len(rrf_results)}"
    )

    # ========================================================
    # STEP 5 — LEGALRAG RERANKING
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 5 — LEGALRAG RERANKING")
    print("-" * 70)

    reranked_results = rerank_results(
        query,
        rrf_results.copy()
    )

    final_results = reranked_results[
        :FINAL_K
    ]

    print(
        f"Final evidence count: "
        f"{len(final_results)}"
    )

    print("\nFinal sections:")

    for i, result in enumerate(
        final_results,
        start=1
    ):

        section = result.get(
            "metadata",
            {}
        ).get(
            "section",
            "Unknown"
        )

        score = result.get(
            "score",
            0
        )

        print(
            f"{i:02d}. Section "
            f"{section} | "
            f"Score={score:.6f}"
        )

    # ========================================================
    # STEP 6 — BUILD LEGAL CONTEXT
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 6 — CONTEXT CONSTRUCTION")
    print("-" * 70)

    context = build_legal_context(
        final_results,
        max_results=FINAL_K
    )

    print(
        f"Context characters: "
        f"{len(context)}"
    )

    # ========================================================
    # STEP 7 — LLM GENERATION
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 7 — LLM GENERATION")
    print("-" * 70)

    answer = generate_answer(
        context,
        query
    )

    print("\nGenerated answer:")
    print(answer)

    # ========================================================
    # STEP 8 — EXTRACT SOURCES
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 8 — SOURCE EXTRACTION")
    print("-" * 70)

    citations = extract_citations(
        final_results
    )

    print(
        f"Sources extracted: "
        f"{len(citations)}"
    )

    # ========================================================
    # STEP 9 — CITATION VERIFICATION
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 9 — CITATION VERIFICATION")
    print("-" * 70)

    grounding = verify_answer_grounding(
        answer,
        final_results
    )

    grounded = grounding.get(
        "grounded",
        False
    )

    citation_verification = grounding.get(
        "citation_verification",
        {}
    )

    print(
        f"Grounded: "
        f"{grounded}"
    )

    print(
        "Citation verification:"
    )

    print(
        citation_verification
    )

    # ========================================================
    # STEP 10 — FINAL RESULT
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 10 — FINAL RESULT")
    print("-" * 70)

    sections = []

    for citation in citations:

        section = str(
            citation.get(
                "section",
                ""
            )
        ).strip()

        if section and section not in sections:

            sections.append(
                section
            )

    result = {

        "query": query,

        "answer": answer,

        "sections": sections,

        "sources": citations,

        "grounded": grounded,

        "citation_verification":
            citation_verification,

        "retrieval_count":
            len(final_results)
    }

    print("\nPipeline complete.")

    print("=" * 70)

    return result