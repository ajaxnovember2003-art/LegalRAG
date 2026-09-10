import re


# ============================================================
# RETRIEVED RESULT CITATIONS
# ============================================================

def extract_citations(results):
    """
    Extract legal citations from retrieved results.

    This function operates on retrieval results and creates
    structured citation metadata for the final answer.
    """

    citations = []

    if not results:
        return citations

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        citation = {
            "document": metadata.get("document"),
            "section": metadata.get("section"),
            "year": metadata.get("year"),
            "source": metadata.get("source")
        }

        if citation not in citations:
            citations.append(citation)

    return citations


# ============================================================
# FORMAT RETRIEVED CITATIONS
# ============================================================

def format_citations(citations):
    """
    Convert structured citation metadata into readable
    source references.
    """

    if not citations:
        return ""

    output = "\n\n### Sources\n"

    for citation in citations:

        output += (
            f"- {citation['document']}, "
            f"Section {citation['section']} "
            f"({citation['year']})"
        )

        output += "\n"

    return output


# ============================================================
# EXTRACT SECTION CITATIONS FROM GENERATED ANSWER
# ============================================================

def extract_section_citations(text):
    """
    Extract section numbers explicitly mentioned in
    an LLM-generated answer.

    Supported forms:

        Section 318
        section 318
        Sec. 318
        §318
        Section 318(1)

    Returns:
        List of unique section numbers.
    """

    if not text:
        return []

    patterns = [

        # Section 318
        r"\bsection\s+(\d+[A-Za-z]?)",

        # Sec. 318
        r"\bsec\.\s*(\d+[A-Za-z]?)",

        # §318
        r"§\s*(\d+[A-Za-z]?)"
    ]

    sections = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for section in matches:

            section = str(
                section
            ).strip()

            if section not in sections:
                sections.append(section)

    return sections


# ============================================================
# EXTRACT SECTIONS FROM RETRIEVED RESULTS
# ============================================================

def get_retrieved_sections(results):
    """
    Extract section numbers from retrieved legal evidence.
    """

    sections = []

    if not results:
        return sections

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        section = str(
            metadata.get(
                "section",
                ""
            )
        ).strip()

        if not section:
            continue

        if section not in sections:
            sections.append(section)

    return sections


# ============================================================
# VERIFY GENERATED CITATIONS
# ============================================================

def verify_citations(
    generated_answer,
    retrieved_results
):
    """
    Verify whether every legal section cited by the
    generated answer exists in the retrieved evidence.

    This performs citation-level verification.

    It does NOT prove that every factual statement in the
    answer is correct.
    """

    cited_sections = extract_section_citations(
        generated_answer
    )

    retrieved_sections = get_retrieved_sections(
        retrieved_results
    )

    supported_sections = []

    unsupported_sections = []

    for section in cited_sections:

        if section in retrieved_sections:

            supported_sections.append(
                section
            )

        else:

            unsupported_sections.append(
                section
            )

    # --------------------------------------------------------
    # NO CITATION
    # --------------------------------------------------------

    if not cited_sections:

        return {
            "verified": False,
            "citation_present": False,
            "cited_sections": [],
            "retrieved_sections": retrieved_sections,
            "supported_sections": [],
            "unsupported_sections": [],
            "reason": (
                "No legal section citation "
                "was found in the generated answer."
            )
        }

    # --------------------------------------------------------
    # UNSUPPORTED CITATION
    # --------------------------------------------------------

    if unsupported_sections:

        return {
            "verified": False,
            "citation_present": True,
            "cited_sections": cited_sections,
            "retrieved_sections": retrieved_sections,
            "supported_sections": supported_sections,
            "unsupported_sections": unsupported_sections,
            "reason": (
                "One or more cited sections "
                "were not present in the retrieved evidence."
            )
        }

    # --------------------------------------------------------
    # ALL CITATIONS SUPPORTED
    # --------------------------------------------------------

    return {
        "verified": True,
        "citation_present": True,
        "cited_sections": cited_sections,
        "retrieved_sections": retrieved_sections,
        "supported_sections": supported_sections,
        "unsupported_sections": [],
        "reason": (
            "All cited sections are present "
            "in the retrieved evidence."
        )
    }


# ============================================================
# ANSWER GROUNDING VERIFICATION
# ============================================================

def verify_answer_grounding(
    generated_answer,
    retrieved_results
):
    """
    Perform citation-level grounding verification.

    A result of grounded=True means every section explicitly
    cited by the generated answer exists in the retrieved
    evidence.

    This should NOT be interpreted as proof that every sentence
    is factually correct.
    """

    citation_result = verify_citations(
        generated_answer,
        retrieved_results
    )

    return {
        "grounded": citation_result["verified"],
        "citation_verification": citation_result
    }