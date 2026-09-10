"""
LegalRAG - Evidence Grounded Generation

Day 24

Responsible for constructing evidence-grounded prompts
and generating answers from retrieved legal evidence.

The LLM is treated as a generation component.
The retrieved legal corpus remains the evidence source.
"""

from typing import Any, Dict, List, Optional


# ============================================================
# CONFIGURATION
# ============================================================

SYSTEM_INSTRUCTION = """
You are a legal information assistant.

Your task is to answer the user's question using ONLY
the legal evidence supplied to you.

Rules:

1. Use the supplied evidence as the factual source.
2. Do not invent legal provisions, sections, punishments,
   procedures, dates, or other legal facts.
3. Do not rely on unstated background knowledge when the
   supplied evidence is insufficient.
4. Clearly identify the relevant legal section when available.
5. Cite the evidence used for the answer.
6. If the evidence is insufficient, explicitly state that
   the available evidence is insufficient.
7. Do not fabricate citations.
8. Distinguish between information explicitly present in
   the evidence and any interpretation.
9. Do not claim that a retrieved section applies to a fact
   pattern unless the supplied evidence supports that claim.
10. Treat the retrieved corpus as the authoritative evidence
    for this response.

Provide concise, legally precise answers.
""".strip()


# ============================================================
# EVIDENCE FORMATTING
# ============================================================

def format_generation_evidence(
    evidence: List[Dict[str, Any]]
) -> str:
    """
    Convert structured evidence into a generation-ready
    evidence block.
    """

    if not evidence:
        return ""

    blocks = []

    for index, item in enumerate(
        evidence,
        start=1
    ):

        section = str(
            item.get(
                "section",
                "Unknown"
            )
        )

        document = str(
            item.get(
                "document",
                "Unknown document"
            )
        )

        year = str(
            item.get(
                "year",
                ""
            )
        )

        source = str(
            item.get(
                "source",
                "Unknown source"
            )
        )

        text = str(
            item.get(
                "text",
                ""
            )
        ).strip()

        block = f"""
[EVIDENCE {index}]

Document: {document}
Year: {year}
Section: {section}
Source: {source}

Legal Text:
{text}
""".strip()

        blocks.append(block)

    return "\n\n".join(blocks)


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_grounded_prompt(
    query: str,
    evidence: List[Dict[str, Any]]
) -> str:
    """
    Build an evidence-grounded user prompt.

    The prompt contains the user's question and the retrieved
    evidence. It does not add external legal information.
    """

    query = str(
        query
    ).strip()

    evidence_text = (
        format_generation_evidence(
            evidence
        )
    )

    if not evidence_text:

        return f"""
USER QUESTION:

{query}

LEGAL EVIDENCE:

No relevant legal evidence was retrieved.

INSTRUCTION:

Do not answer using general knowledge.
State that the available legal evidence is insufficient.
""".strip()

    return f"""
USER QUESTION:

{query}

LEGAL EVIDENCE:

{evidence_text}

TASK:

Answer the user's question using only the supplied
legal evidence.

Your response must contain:

1. Answer
2. Legal Basis
3. Sources

If the evidence does not provide enough information,
say so explicitly.

Do not fabricate missing information or citations.
""".strip()


# ============================================================
# GENERATION PAYLOAD
# ============================================================

def build_generation_payload(
    query: str,
    evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build a provider-independent generation payload.

    This keeps the generation layer separate from the
    specific LLM provider.
    """

    return {
        "system_instruction": SYSTEM_INSTRUCTION,
        "prompt": build_grounded_prompt(
            query,
            evidence
        ),
        "evidence_count": len(evidence),
    }


# ============================================================
# FALLBACK RESPONSE
# ============================================================

def insufficient_evidence_response() -> Dict[str, Any]:
    """
    Safe response when no usable legal evidence exists.
    """

    return {
        "answer": (
            "The available legal evidence is insufficient "
            "to answer this question reliably."
        ),
        "legal_basis": "",
        "sources": [],
        "grounded": False,
    }


# ============================================================
# GENERATION RESULT NORMALIZATION
# ============================================================

def normalize_generation_result(
    generated_text: str,
    evidence: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Normalize raw LLM output into a consistent structure.

    Citation validation will be implemented in a later stage.
    """

    generated_text = str(
        generated_text or ""
    ).strip()

    sources = []

    for index, item in enumerate(
        evidence,
        start=1
    ):

        sources.append({
            "id": index,
            "section": item.get(
                "section",
                "Unknown"
            ),
            "document": item.get(
                "document",
                "Unknown document"
            ),
            "year": item.get(
                "year",
                ""
            ),
            "source": item.get(
                "source",
                "Unknown source"
            ),
        })

    return {
        "answer": generated_text,
        "evidence_count": len(evidence),
        "sources": sources,
        "grounded": bool(
            generated_text
            and evidence
        ),
    }