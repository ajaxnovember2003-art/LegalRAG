import re


def extract_citations(results):
    """
    Extract legal citations from retrieved results.
    """

    citations = []

    for result in results:

        metadata = result["metadata"]

        citation = {
            "document": metadata.get("document"),
            "section": metadata.get("section"),
            "year": metadata.get("year"),
            "source": metadata.get("source")
        }

        if citation not in citations:
            citations.append(citation)

    return citations


def format_citations(citations):

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