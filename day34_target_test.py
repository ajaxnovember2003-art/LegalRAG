from backend.app.services.hybrid_retrieval import detect_offence, LEGAL_DISTINCTIONS

queries = {
    3: "A person takes property from another while using violence or creating fear of immediate harm. Which provision applies?",
    4: "Property is taken from a victim after the offender threatens the victim with immediate physical harm. Identify the relevant legal provision.",
    5: "A group of five or more persons jointly commits robbery. Which legal provision governs the offence?",
    6: "Five or more individuals participate together in taking property through robbery. Identify the applicable provision.",
    7: "A person threatens another with injury and dishonestly induces them to hand over property. Which provision applies?",
    10: "Someone lawfully receives property under a position of trust but later dishonestly uses the property as their own. Identify the applicable provision.",
}

for qid, query in queries.items():
    offence = detect_offence(query)

    print("=" * 70)
    print(f"Q{qid}")
    print(f"Query: {query}")
    print(f"Detected offence: {offence}")

    if offence:
        print("Positive rules matched:")
        for phrase in LEGAL_DISTINCTIONS.get(offence, {}).get("positive", []):
            if phrase.lower() in query.lower():
                print(f"  + {phrase}")

        print("Negative rules matched:")
        for phrase in LEGAL_DISTINCTIONS.get(offence, {}).get("negative", []):
            if phrase.lower() in query.lower():
                print(f"  - {phrase}")
