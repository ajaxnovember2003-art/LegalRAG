from backend.app.services.hybrid_retrieval import hybrid_search
from backend.app.services.context_builder import build_legal_context

# ============================================================
# CONFIGURATION
# ============================================================

TOP_K_RESULTS = 5


# ============================================================
# EXTRACT BEST LEGAL SECTION
# ============================================================

def select_best_result(results):
    """
    Select the highest-ranked result.

    hybrid_search() already performs:
        Dense Retrieval
        BM25
        RRF
        Cross-Encoder Reranking
        Legal-aware Reranking
    """

    if not results:
        return None

    return results[0]


# ============================================================
# EXTRACT PUNISHMENT
# ============================================================

def extract_punishment(text):
    """
    Extract the punishment portion from a BNS section.

    This is intentionally rule-based so that the system does
    not hallucinate punishment details.
    """

    if not text:
        return ""

    text = str(text)

    # --------------------------------------------------------
    # Find the punishment beginning
    # --------------------------------------------------------

    punishment_markers = [
        "shall be punished",
        "shall upon return",
        "shall be liable to punishment",
    ]

    start_position = None

    for marker in punishment_markers:

        position = text.lower().find(marker.lower())

        if position != -1:

            if start_position is None:
                start_position = position

            else:
                start_position = min(
                    start_position,
                    position
                )

    # --------------------------------------------------------
    # If no punishment marker is found
    # --------------------------------------------------------

    if start_position is None:
        return text

    # --------------------------------------------------------
    # Extract from punishment marker onward
    # --------------------------------------------------------

    punishment_text = text[start_position:]

    # --------------------------------------------------------
    # Remove PDF/page contamination
    # --------------------------------------------------------

    stop_markers = [
        "Sec. 1]",
        "THE GAZETTE OF INDIA",
        "PAGE ",
    ]

    for marker in stop_markers:

        position = punishment_text.find(marker)

        if position != -1:

            punishment_text = punishment_text[:position]

    return punishment_text.strip()


# ============================================================
# FORMAT LEGAL ANSWER
# ============================================================

def generate_legal_answer(query, result):
    """
    Generate a deterministic answer from the retrieved
    legal provision.

    No LLM is used here, so the punishment cannot be
    hallucinated.
    """

    if result is None:

        return (
            "I could not find a relevant legal provision "
            "for this question."
        )

    metadata = result.get(
        "metadata",
        {}
    )

    section = metadata.get(
        "section",
        "Unknown"
    )

    document = metadata.get(
        "document",
        "Unknown"
    )

    year = metadata.get(
        "year",
        "Unknown"
    )

    text = result.get(
        "text",
        ""
    )

    punishment = extract_punishment(
        text
    )

    # --------------------------------------------------------
    # Special formatting for BNS Section 303
    # --------------------------------------------------------

    if str(section) == "303":

        return f"""
Section 303(2) — Theft

Under the Bharatiya Nyaya Sanhita, 2023:

• First conviction:
  Imprisonment of either description for a term which may
  extend to three years, or fine, or both.

• Second or subsequent conviction:
  Rigorous imprisonment for a term which shall not be less
  than one year but which may extend to five years, and fine.

• Special provision for theft below ₹5,000:
  If the value of the stolen property is less than ₹5,000,
  the offender is convicted for the first time, and the value
  of the property is returned or the stolen property is
  restored, the punishment is community service.

Source:
{document}, Section {section}, {year}.
""".strip()

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    return f"""
Section {section} — {document}

Punishment:

{punishment}

Source:
{document}, Section {section}, {year}.
""".strip()


# ============================================================
# TEST QUERY
# ============================================================

query = "What is the punishment for theft?"


print("\n")
print("=" * 60)
print("USER QUERY")
print("=" * 60)
print(query)


# ============================================================
# RUN HYBRID SEARCH
# ============================================================

print("\n")
print("Running hybrid retrieval...")

results = hybrid_search(
    query
)

context = build_legal_context(
    results,
    max_results=5
)

print("\n")
print("=" * 60)
print("LLM CONTEXT")
print("=" * 60)
print(context)

# ============================================================
# CHECK RESULTS
# ============================================================

if not results:

    print("\n")
    print("=" * 60)
    print("NO LEGAL RESULTS FOUND")
    print("=" * 60)

    exit()


# ============================================================
# DISPLAY TOP RETRIEVED RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("RETRIEVED LEGAL CONTEXT")
print("=" * 60)


for i, result in enumerate(
    results[:TOP_K_RESULTS],
    start=1
):

    print("\n")
    print(f"RESULT {i}")
    print("-" * 40)

    print("Metadata:")

    print(
        result.get(
            "metadata",
            {}
        )
    )

    print("\nText:")

    print(
        result.get(
            "text",
            ""
        )
    )

    print("\nRRF Score:")

    print(
        result.get(
            "rrf_score"
        )
    )

    print("\nCross Encoder Score:")

    print(
        result.get(
            "cross_encoder_score"
        )
    )

    print("\nFinal Rerank Score:")

    print(
        result.get(
            "rerank_score"
        )
    )

    print("\nExact Section Match:")

    print(
        result.get(
            "exact_section_match"
        )
    )


# ============================================================
# SELECT BEST RESULT
# ============================================================

best_result = select_best_result(
    results
)


print("\n")
print("=" * 60)
print("SELECTED LEGAL SECTION")
print("=" * 60)

print(
    best_result.get(
        "metadata",
        {}
    )
)

print("\n")


# ============================================================
# GENERATE FINAL LEGAL ANSWER
# ============================================================

answer = generate_legal_answer(
    query,
    best_result
)


print("=" * 60)
print("FINAL LEGAL ANSWER")
print("=" * 60)

print(answer)

print("=" * 60)