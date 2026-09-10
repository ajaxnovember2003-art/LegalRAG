"""
LegalRAG - Legal Context Utilities
------

Utilities for identifying legal sections and extracting
specific legal information from retrieved provisions.

Important:
    These functions operate only on retrieved text.
    They do not generate legal conclusions.
"""

import re
from typing import Any, Dict, List, Optional


# ============================================================
# SECTION EXTRACTION
# ============================================================

def extract_section_number(
    text: str
) -> Optional[str]:
    """
    Extract a section number from the beginning of a legal chunk.

    Examples:

        '303. (1) Whoever...' -> '303'
        '318. Whoever...'    -> '318'
    """

    if not text:
        return None

    match = re.match(
        r"^\s*(\d+)\.",
        text
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# OFFENCE → PRIMARY SECTION MAPPING
# ============================================================

PRIMARY_OFFENCE_SECTIONS = {

    "theft": "303",

    "snatching": "304",

}


# ============================================================
# SECTION LOOKUP
# ============================================================

def find_section_result(
    results: List[Dict[str, Any]],
    target_section: str
) -> Optional[Dict[str, Any]]:
    """
    Find a retrieval result matching an exact section.
    """

    if not results:
        return None

    target_section = str(
        target_section
    ).strip()

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

        if section == target_section:
            return result

    return None


# ============================================================
# OFFENCE SECTION SELECTION
# ============================================================

def select_relevant_section(
    results: List[Dict[str, Any]],
    detected_offence: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Select the most relevant legal section.

    Priority:

        1. Explicit offence → section mapping
        2. Exact definition match
        3. Section metadata match
        4. First ranked retrieval result
    """

    if not results:
        return None

    # --------------------------------------------------------
    # 1. Explicit mapping
    # --------------------------------------------------------

    if detected_offence:

        offence = (
            detected_offence
            .strip()
            .lower()
        )

        target_section = (
            PRIMARY_OFFENCE_SECTIONS
            .get(offence)
        )

        if target_section:

            result = find_section_result(
                results,
                target_section
            )

            if result is not None:
                return result

    # --------------------------------------------------------
    # 2. Definition matching
    # --------------------------------------------------------

    if detected_offence:

        offence = (
            detected_offence
            .strip()
            .lower()
        )

        escaped = re.escape(
            offence
        )

        definition_patterns = [

            rf"\bis\s+said\s+to\s+commit\s+{escaped}\b",

            rf"\bis\s+{escaped}\b",

            rf"\bwhoever\s+commits\s+{escaped}\b",

            rf"\bcommits\s+{escaped}\b",

        ]

        for result in results:

            text = result.get(
                "text",
                ""
            ).lower()

            for pattern in definition_patterns:

                if re.search(
                    pattern,
                    text
                ):
                    return result

    # --------------------------------------------------------
    # 3. First ranked result
    # --------------------------------------------------------

    return results[0]


# ============================================================
# PUNISHMENT EXTRACTION
# ============================================================

def extract_punishment_text(
    text: str
) -> str:
    """
    Extract the punishment statement from a retrieved
    legal provision.

    The function only extracts existing text.
    """

    if not text:
        return ""

    match = re.search(
        r"(shall\s+be\s+punished\b.*)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return ""

    punishment = (
        match.group(1)
        .strip()
    )

    # Remove contamination from the next section
    punishment = re.split(
        r"\bSEC\.\s*\d+\b",
        punishment,
        flags=re.IGNORECASE
    )[0]

    return punishment.strip()


# ============================================================
# LEGAL EVIDENCE EXTRACTION
# ============================================================

def extract_legal_evidence(
    result: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract a standardized legal evidence record from
    one retrieval result.
    """

    if result is None:
        return {}

    metadata = result.get(
        "metadata",
        {}
    )

    text = result.get(
        "text",
        ""
    )

    section = str(
        metadata.get(
            "section",
            ""
        )
    ).strip()

    return {
        "section": section,
        "document": metadata.get(
            "document",
            "Unknown document"
        ),
        "year": metadata.get(
            "year",
            ""
        ),
        "source": metadata.get(
            "source",
            "Unknown source"
        ),
        "text": text,
        "punishment": extract_punishment_text(
            text
        ),
        "retrieval_score": result.get(
            "score"
        )
    }