from backend.app.services.generation import (
    build_generation_payload,
    insufficient_evidence_response
)


def main():

    query = (
        "What is the punishment for cheating?"
    )

    evidence = [

        {
            "section": "318",
            "document": "Bharatiya Nyaya Sanhita",
            "year": "2023",
            "source": "Legal Corpus",
            "text": (
                "318. Whoever cheats and thereby "
                "dishonestly induces the person deceived "
                "to deliver any property..."
            )
        },

        {
            "section": "322",
            "document": "Bharatiya Nyaya Sanhita",
            "year": "2023",
            "source": "Legal Corpus",
            "text": (
                "322. Whoever dishonestly receives "
                "property..."
            )
        }
    ]

    # --------------------------------------------------------
    # BUILD PAYLOAD
    # --------------------------------------------------------

    payload = build_generation_payload(
        query,
        evidence
    )

    print("\n" + "=" * 70)
    print("DAY 24 - GENERATION PAYLOAD")
    print("=" * 70)

    print("\nSYSTEM INSTRUCTION:")
    print(
        payload["system_instruction"]
    )

    print("\nUSER PROMPT:")
    print(
        payload["prompt"]
    )

    print("\nEvidence count:")
    print(
        payload["evidence_count"]
    )

    # --------------------------------------------------------
    # EMPTY EVIDENCE TEST
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("NO-EVIDENCE TEST")
    print("=" * 70)

    empty_payload = build_generation_payload(
        query,
        []
    )

    print(
        empty_payload["prompt"]
    )

    fallback = (
        insufficient_evidence_response()
    )

    print("\nFallback response:")
    print(
        fallback
    )


if __name__ == "__main__":
    main()