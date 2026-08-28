import re


def extract_section_number(text):
    """
    Extract section number from the beginning of a legal chunk.

    Example:
        '303. (1) Whoever...' -> '303'
    """

    if not text:
        return None

    match = re.match(r"^\s*(\d+)\.", text)

    if match:
        return match.group(1)

    return None


# ============================================================
# OFFENCE -> PRIMARY SECTION MAPPING
# ============================================================

PRIMARY_OFFENCE_SECTIONS = {
    "theft": "303",
    "snatching": "304",
}


def select_relevant_section(results, detected_offence=None):
    """
    Select the primary legal section for the detected offence.

    Priority:
    1. Explicit offence-to-section mapping
    2. Exact section metadata match
    3. Strong definition match
    4. First result fallback
    """

    if not results:
        return None

    # --------------------------------------------------------
    # 1. Use explicit offence -> primary section mapping
    # --------------------------------------------------------

    if detected_offence:

        offence = detected_offence.strip().lower()

        target_section = PRIMARY_OFFENCE_SECTIONS.get(offence)

        if target_section:

            for result in results:

                metadata = result.get("metadata", {})

                section = str(
                    metadata.get("section", "")
                ).strip()

                if section == target_section:
                    return result

    # --------------------------------------------------------
    # 2. Look for a result whose section text DEFINES
    #    the offence rather than merely mentioning it
    # --------------------------------------------------------

    if detected_offence:

        offence = detected_offence.strip().lower()

        definition_patterns = [
            rf"is said to commit {re.escape(offence)}",
            rf"is {re.escape(offence)}",
            rf"whoever commits {re.escape(offence)}",
            rf"commits {re.escape(offence)}",
        ]

        for result in results:

            text = result.get("text", "").lower()

            for pattern in definition_patterns:

                if re.search(pattern, text):

                    return result

    # --------------------------------------------------------
    # 3. Fallback
    # --------------------------------------------------------

    return results[0]


# ============================================================
# PUNISHMENT EXTRACTION
# ============================================================

def extract_punishment_text(text):
    """
    Extract the punishment portion of a legal section.

    Handles:
        shall be punished...
        Provided that...
        second/subsequent conviction...
    """

    if not text:
        return ""

    # --------------------------------------------------------
    # Find punishment statement
    # --------------------------------------------------------

    match = re.search(
        r"(shall\s+be\s+punished\b.*)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        punishment = match.group(1).strip()

        # Remove obvious PDF page/header contamination
        punishment = re.split(
            r"\bSEC\.\s*\d+\b",
            punishment,
            flags=re.IGNORECASE
        )[0]

        return punishment.strip()

    return ""