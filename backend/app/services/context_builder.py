"""
LegalRAG - Context Builder
------
Converts ranked retrieval results into a structured,
traceable legal evidence context for downstream LLM generation.

Responsibilities:
    1. Clean retrieved evidence
    2. Remove duplicate sections
    3. Preserve provenance
    4. Preserve retrieval scores/ranks
    5. Enforce context limits
    6. Produce both structured and formatted context
"""

from typing import Any, Dict, List, Optional


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MAX_RESULTS = 5
DEFAULT_MAX_CHARS_PER_CHUNK = 6000


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: Any) -> str:
    """
    Clean retrieved legal text without changing its meaning.
    """

    if text is None:
        return ""

    text = str(text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    lines = []

    for line in text.split("\n"):
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


# ============================================================
# METADATA EXTRACTION
# ============================================================

def get_metadata(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely extract metadata from a retrieval result.
    """

    metadata = result.get("metadata", {})

    if not isinstance(metadata, dict):
        return {}

    return metadata


def get_section(result: Dict[str, Any]) -> str:
    """
    Extract section number.
    """

    metadata = get_metadata(result)

    return str(
        metadata.get("section", "")
    ).strip()


def get_document(result: Dict[str, Any]) -> str:
    """
    Extract document name.
    """

    metadata = get_metadata(result)

    return str(
        metadata.get(
            "document",
            "Unknown document"
        )
    ).strip()


def get_source(result: Dict[str, Any]) -> str:
    """
    Extract source information.
    """

    metadata = get_metadata(result)

    return str(
        metadata.get(
            "source",
            "Unknown source"
        )
    ).strip()


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def section_key(result: Dict[str, Any]):
    """
    Generate a stable identifier for a legal provision.

    Document + section is used because the same section number
    can theoretically occur in different legal documents.
    """

    metadata = get_metadata(result)

    document = str(
        metadata.get(
            "document",
            "Unknown document"
        )
    ).strip()

    section = str(
        metadata.get(
            "section",
            ""
        )
    ).strip()

    source = str(
        metadata.get(
            "source",
            ""
        )
    ).strip()

    return (
        document,
        section,
        source
    )


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_result(
    result: Dict[str, Any],
    rank: int
) -> Optional[Dict[str, Any]]:
    """
    Convert one raw retrieval result into a standardized
    evidence object.

    This function does not generate or alter legal facts.
    """

    if not isinstance(result, dict):
        return None

    text = clean_text(
        result.get("text", "")
    )

    if not text:
        return None

    metadata = get_metadata(result)

    section = str(
        metadata.get(
            "section",
            "Unknown"
        )
    ).strip()

    document = str(
        metadata.get(
            "document",
            "Unknown document"
        )
    ).strip()

    source = str(
        metadata.get(
            "source",
            "Unknown source"
        )
    ).strip()

    year = str(
        metadata.get(
            "year",
            ""
        )
    ).strip()

    # Preserve retrieval score when available
    score = result.get(
        "score",
        None
    )

    # Preserve the query responsible for ranking
    best_query = result.get(
        "best_query",
        None
    )

    # Preserve original rank if available
    original_rank = result.get(
        "best_rank",
        rank
    )

    return {
        "rank": rank,
        "original_rank": original_rank,
        "section": section,
        "document": document,
        "year": year,
        "source": source,
        "text": text,
        "retrieval_score": score,
        "best_query": best_query,
    }


# ============================================================
# BUILD STRUCTURED EVIDENCE
# ============================================================

def build_evidence(
    results: List[Dict[str, Any]],
    max_results: int = DEFAULT_MAX_RESULTS,
    max_chars_per_chunk: int = DEFAULT_MAX_CHARS_PER_CHUNK
) -> List[Dict[str, Any]]:
    """
    Convert retrieval results into unique, structured
    legal evidence.

    Duplicate legal sections are removed while preserving
    the highest-ranked occurrence.
    """

    if not results:
        return []

    evidence = []

    seen = set()

    for result in results:

        if len(evidence) >= max_results:
            break

        key = section_key(result)

        if key in seen:
            continue

        normalized = normalize_result(
            result,
            rank=len(evidence) + 1
        )

        if normalized is None:
            continue

        text = normalized["text"]

        # Context protection
        if (
            max_chars_per_chunk is not None
            and len(text) > max_chars_per_chunk
        ):
            text = text[
                :max_chars_per_chunk
            ].rstrip()

            normalized["text"] = text
            normalized["truncated"] = True

        else:
            normalized["truncated"] = False

        seen.add(key)

        evidence.append(
            normalized
        )

    return evidence


# ============================================================
# BUILD LLM CONTEXT
# ============================================================

def format_evidence(
    evidence: List[Dict[str, Any]]
) -> str:
    """
    Convert structured evidence into a deterministic textual
    context for the downstream LLM.

    The legal text itself is preserved.
    """

    if not evidence:
        return ""

    context_parts = []

    for item in evidence:

        rank = item.get(
            "rank",
            "?"
        )

        document = item.get(
            "document",
            "Unknown document"
        )

        year = item.get(
            "year",
            ""
        )

        section = item.get(
            "section",
            "Unknown"
        )

        source = item.get(
            "source",
            "Unknown source"
        )

        score = item.get(
            "retrieval_score",
            None
        )

        text = item.get(
            "text",
            ""
        )

        if isinstance(score, float):
            score_text = f"{score:.6f}"
        else:
            score_text = str(score)

        source_block = f"""
SOURCE {rank}

Document: {document}
Year: {year}
Section: {section}
Source: {source}
Retrieval Score: {score_text}

Legal Text:
{text}
""".strip()

        context_parts.append(
            source_block
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# MAIN CONTEXT BUILDER
# ============================================================

def build_legal_context(
    results: List[Dict[str, Any]],
    max_results: int = DEFAULT_MAX_RESULTS,
    max_chars_per_chunk: int = DEFAULT_MAX_CHARS_PER_CHUNK
) -> str:
    """
    Main public interface.

    Converts ranked retrieval results into a clean,
    provenance-preserving textual context for the LLM.
    """

    evidence = build_evidence(
        results,
        max_results=max_results,
        max_chars_per_chunk=max_chars_per_chunk
    )

    return format_evidence(
        evidence
    )


# ============================================================
# STRUCTURED CONTEXT
# ============================================================

def build_structured_legal_context(
    query: str,
    results: List[Dict[str, Any]],
    max_results: int = DEFAULT_MAX_RESULTS,
    max_chars_per_chunk: int = DEFAULT_MAX_CHARS_PER_CHUNK
) -> Dict[str, Any]:
    """
    Build a structured legal context object.

    This is useful for:
        - LLM generation
        - citation generation
        - evaluation
        - debugging
        - frontend/API responses
    """

    evidence = build_evidence(
        results,
        max_results=max_results,
        max_chars_per_chunk=max_chars_per_chunk
    )

    return {
        "query": query,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "formatted_context": format_evidence(
            evidence
        )
    }


# ============================================================
# DEBUGGING
# ============================================================

def print_context_summary(
    context: Dict[str, Any]
) -> None:
    """
    Print a human-readable summary of structured evidence.
    """

    print("\n" + "=" * 70)
    print("LEGAL CONTEXT SUMMARY")
    print("=" * 70)

    print(
        f"Query: {context.get('query', '')}"
    )

    print(
        f"Evidence count: "
        f"{context.get('evidence_count', 0)}"
    )

    print("\nEvidence:")

    for item in context.get(
        "evidence",
        []
    ):

        print(
            f"  Rank {item.get('rank')}: "
            f"Section {item.get('section')} "
            f"| Score={item.get('retrieval_score')}"
        )

    print("=" * 70)