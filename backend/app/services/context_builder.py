def build_legal_context(results, max_results=5):
    """
    Convert retrieved legal documents into a clean context
    for the LLM.
    """

    if not results:
        return ""

    context_parts = []

    seen_sections = set()

    for result in results[:max_results]:

        metadata = result.get("metadata", {})
        text = result.get("text", "").strip()

        section = str(
            metadata.get("section", "Unknown")
        ).strip()

        document = metadata.get(
            "document",
            "Unknown document"
        )

        year = metadata.get(
            "year",
            ""
        )

        # Avoid duplicate sections
        section_key = (
            document,
            section
        )

        if section_key in seen_sections:
            continue

        seen_sections.add(section_key)

        context_parts.append(
            f"""
SOURCE {len(context_parts) + 1}

Document: {document}
Year: {year}
Section: {section}

Text:
{text}
""".strip()
        )

    return "\n\n".join(context_parts)