from backend.app.services.citation import (
    extract_citations,
    format_citations,
    extract_section_citations,
    get_retrieved_sections,
    verify_citations,
    verify_answer_grounding
)


# ============================================================
# TEST DATA
# ============================================================

retrieved_results = [

    {
        "text": (
            "318. Whoever cheats and thereby dishonestly "
            "induces the person deceived to deliver property..."
        ),
        "metadata": {
            "document": "Bharatiya Nyaya Sanhita",
            "year": 2023,
            "section": "318",
            "source": "Legal Corpus"
        },
        "score": 0.683060
    },

    {
        "text": (
            "322. Whoever dishonestly receives property..."
        ),
        "metadata": {
            "document": "Bharatiya Nyaya Sanhita",
            "year": 2023,
            "section": "322",
            "source": "Legal Corpus"
        },
        "score": 0.248413
    },

    {
        "text": (
            "317. Whoever dishonestly misappropriates..."
        ),
        "metadata": {
            "document": "Bharatiya Nyaya Sanhita",
            "year": 2023,
            "section": "317",
            "source": "Legal Corpus"
        },
        "score": 0.247676
    }
]


# ============================================================
# TEST 1
# ============================================================

print("=" * 70)
print("TEST 1 - EXISTING CITATION EXTRACTION")
print("=" * 70)

citations = extract_citations(
    retrieved_results
)

print("Extracted citations:")

for citation in citations:
    print(citation)


# ============================================================
# TEST 2
# ============================================================

print("\n" + "=" * 70)
print("TEST 2 - CITATION FORMATTING")
print("=" * 70)

formatted = format_citations(
    citations
)

print(formatted)


# ============================================================
# TEST 3
# ============================================================

print("\n" + "=" * 70)
print("TEST 3 - LLM CITATION EXTRACTION")
print("=" * 70)

generated_answer = """
Section 318 — Cheating

The retrieved legal evidence identifies cheating
under Section 318.

Source: Section 318
"""

cited_sections = extract_section_citations(
    generated_answer
)

print("Sections cited by LLM:")
print(cited_sections)


# ============================================================
# TEST 4
# ============================================================

print("\n" + "=" * 70)
print("TEST 4 - RETRIEVED SECTION EXTRACTION")
print("=" * 70)

retrieved_sections = get_retrieved_sections(
    retrieved_results
)

print("Sections present in evidence:")
print(retrieved_sections)


# ============================================================
# TEST 5
# ============================================================

print("\n" + "=" * 70)
print("TEST 5 - VALID CITATION")
print("=" * 70)

result = verify_citations(
    generated_answer,
    retrieved_results
)

print(result)


# ============================================================
# TEST 6
# ============================================================

print("\n" + "=" * 70)
print("TEST 6 - INVALID / HALLUCINATED CITATION")
print("=" * 70)

invalid_answer = """
Section 420 — Cheating

The offence is covered under Section 420.

Source: Section 420
"""

result = verify_citations(
    invalid_answer,
    retrieved_results
)

print(result)


# ============================================================
# TEST 7
# ============================================================

print("\n" + "=" * 70)
print("TEST 7 - MIXED VALID AND INVALID CITATIONS")
print("=" * 70)

mixed_answer = """
Sections 318 and 420 are relevant to this question.
"""

result = verify_citations(
    mixed_answer,
    retrieved_results
)

print(result)


# ============================================================
# TEST 8
# ============================================================

print("\n" + "=" * 70)
print("TEST 8 - NO CITATION")
print("=" * 70)

no_citation_answer = """
The retrieved evidence discusses cheating and
dishonest inducement involving property.
"""

result = verify_citations(
    no_citation_answer,
    retrieved_results
)

print(result)


# ============================================================
# TEST 9
# ============================================================

print("\n" + "=" * 70)
print("TEST 9 - GROUNDING VERIFICATION")
print("=" * 70)

grounding_result = verify_answer_grounding(
    generated_answer,
    retrieved_results
)

print(grounding_result)


print("\n" + "=" * 70)
print("DAY 25 CITATION VERIFICATION TEST COMPLETE")
print("=" * 70)
