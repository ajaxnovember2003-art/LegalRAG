from backend.app.services.context_builder import (
    build_legal_context,
    build_structured_legal_context,
    print_context_summary
)


def main():

    results = [

        {
            "text": (
                "318. Whoever cheats and thereby "
                "dishonestly induces the person deceived "
                "to deliver any property..."
            ),

            "metadata": {
                "section": "318",
                "document": "Bharatiya Nyaya Sanhita",
                "year": "2023",
                "source": "Legal Corpus"
            },

            "score": 0.683060
        },

        {
            "text": (
                "322. Whoever dishonestly receives "
                "property..."
            ),

            "metadata": {
                "section": "322",
                "document": "Bharatiya Nyaya Sanhita",
                "year": "2023",
                "source": "Legal Corpus"
            },

            "score": 0.248413
        },

        {
            "text": (
                "317. Whoever dishonestly misappropriates..."
            ),

            "metadata": {
                "section": "317",
                "document": "Bharatiya Nyaya Sanhita",
                "year": "2023",
                "source": "Legal Corpus"
            },

            "score": 0.247676
        }
    ]

    query = (
        "What is the punishment for cheating?"
    )

    # --------------------------------------------------------
    # STRUCTURED CONTEXT
    # --------------------------------------------------------

    structured = (
        build_structured_legal_context(
            query,
            results,
            max_results=5
        )
    )

    print_context_summary(
        structured
    )

    # --------------------------------------------------------
    # FORMATTED CONTEXT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LLM CONTEXT")
    print("=" * 70)

    print(
        build_legal_context(
            results,
            max_results=5
        )
    )


if __name__ == "__main__":
    main()