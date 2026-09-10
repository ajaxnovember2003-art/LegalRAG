# ============================================================
# LegalRAG - Day 27
# Hard / Leakage-Resistant Evaluation Dataset
# ============================================================

HARD_QUERIES = [

    # ========================================================
    # THEFT - Section 303
    # ========================================================

    {
        "query": (
            "A person dishonestly takes movable property out of "
            "another person's possession without that person's consent. "
            "Which legal provision applies?"
        ),
        "expected_section": "303"
    },

    {
        "query": (
            "Someone secretly removes another person's movable property "
            "from their possession with dishonest intention and without consent. "
            "Identify the applicable provision."
        ),
        "expected_section": "303"
    },

    # ========================================================
    # ROBBERY - Section 309
    # ========================================================

    {
        "query": (
            "A person takes property from another while using violence "
            "or creating fear of immediate harm. Which provision applies?"
        ),
        "expected_section": "309"
    },

    {
        "query": (
            "Property is taken from a victim after the offender threatens "
            "the victim with immediate physical harm. Identify the relevant "
            "legal provision."
        ),
        "expected_section": "309"
    },

    # ========================================================
    # DACOITY - Section 310
    # ========================================================

    {
        "query": (
            "A group of five or more persons jointly commits robbery. "
            "Which legal provision governs the offence?"
        ),
        "expected_section": "310"
    },

    {
        "query": (
            "Five or more individuals participate together in taking "
            "property through robbery. Identify the applicable provision."
        ),
        "expected_section": "310"
    },

    # ========================================================
    # EXTORTION - Section 308
    # ========================================================

    {
        "query": (
            "A person threatens another with injury and dishonestly "
            "induces them to hand over property. Which provision applies?"
        ),
        "expected_section": "308"
    },

    {
        "query": (
            "Someone creates fear of harm in another person and uses "
            "that fear to obtain delivery of property. Identify the "
            "relevant legal provision."
        ),
        "expected_section": "308"
    },

    # ========================================================
    # CRIMINAL BREACH OF TRUST - Section 316
    # ========================================================

    {
        "query": (
            "A person is entrusted with property or control over it "
            "and dishonestly converts or misappropriates that property. "
            "Which provision applies?"
        ),
        "expected_section": "316"
    },

    {
        "query": (
            "Someone lawfully receives property under a position of trust "
            "but later dishonestly uses the property as their own. "
            "Identify the applicable provision."
        ),
        "expected_section": "316"
    },

    # ========================================================
    # RECEIVING STOLEN PROPERTY - Section 317
    # ========================================================

    {
        "query": (
            "A person knowingly receives or retains property that was "
            "obtained through an offence. Which legal provision applies?"
        ),
        "expected_section": "317"
    },

    {
        "query": (
            "Someone purchases and keeps property while knowing, or having "
            "reason to believe, that the property was unlawfully obtained. "
            "Identify the applicable provision."
        ),
        "expected_section": "317"
    },

    # ========================================================
    # CHEATING - Section 318
    # ========================================================

    {
        "query": (
            "A person deliberately deceives another and dishonestly "
            "induces that person to deliver property. Which provision applies?"
        ),
        "expected_section": "318"
    },

    {
        "query": (
            "Someone uses deception to cause another person to transfer "
            "property to them dishonestly. Identify the relevant provision."
        ),
        "expected_section": "318"
    },

    # ========================================================
    # MURDER - Section 103
    # ========================================================

    {
        "query": (
            "A person intentionally causes the death of another person. "
            "Which legal provision applies?"
        ),
        "expected_section": "103"
    },

    {
        "query": (
            "An individual causes another person's death with the intention "
            "of causing death. Identify the applicable provision."
        ),
        "expected_section": "103"
    },

    # ========================================================
    # CULPABLE HOMICIDE - Section 105
    # ========================================================

    {
        "query": (
            "A person causes death with the intention of causing death, "
            "or with knowledge that the act is likely to cause death. "
            "Which provision applies?"
        ),
        "expected_section": "105"
    },

    {
        "query": (
            "Someone performs an act that causes death while possessing "
            "the required intention or knowledge regarding the likelihood "
            "of death. Identify the relevant provision."
        ),
        "expected_section": "105"
    },

    # ========================================================
    # ATTEMPT TO MURDER - Section 109
    # ========================================================

    {
        "query": (
            "A person performs an act towards causing another person's "
            "death with the necessary intention or knowledge, but death "
            "does not occur. Which provision applies?"
        ),
        "expected_section": "109"
    },

    {
        "query": (
            "Someone takes a direct step toward causing the death of "
            "another person with the required intention, but the victim "
            "survives. Identify the applicable provision."
        ),
        "expected_section": "109"
    },

    # ========================================================
    # CRIMINAL INTIMIDATION - Section 351
    # ========================================================

    {
        "query": (
            "A person threatens another with injury to their person, "
            "reputation, or property in order to cause alarm. "
            "Which provision applies?"
        ),
        "expected_section": "351"
    },

    {
        "query": (
            "Someone threatens another individual with harm to their "
            "reputation or property with the intention of causing fear. "
            "Identify the relevant provision."
        ),
        "expected_section": "351"
    },

    # ========================================================
    # WRONGFUL RESTRAINT - Section 126
    # ========================================================

    {
        "query": (
            "A person voluntarily obstructs another individual so that "
            "the person cannot proceed in a direction in which they have "
            "a right to proceed. Which provision applies?"
        ),
        "expected_section": "126"
    },

    # ========================================================
    # WRONGFUL CONFINEMENT - Section 127
    # ========================================================

    {
        "query": (
            "A person intentionally prevents another individual from "
            "leaving a restricted area or from moving beyond certain limits. "
            "Which provision applies?"
        ),
        "expected_section": "127"
    },

    # ========================================================
    # RAPE - Section 64
    # ========================================================

    {
        "query": (
            "A person engages in sexual intercourse with another person "
            "without that person's consent under circumstances covered "
            "by the offence. Which provision applies?"
        ),
        "expected_section": "64"
    },

    # ========================================================
    # SEXUAL HARASSMENT - Section 75
    # ========================================================

    {
        "query": (
            "A person makes unwelcome sexual remarks or engages in "
            "unwelcome sexual behaviour toward another person. "
            "Which provision applies?"
        ),
        "expected_section": "75"
    },
]


# ============================================================
# BASIC VALIDATION
# ============================================================

def validate_dataset():

    print("=" * 70)
    print("LegalRAG Day 27 - Hard Benchmark")
    print("=" * 70)

    print(f"Total queries: {len(HARD_QUERIES)}")

    missing = []

    for i, item in enumerate(HARD_QUERIES, start=1):

        if "query" not in item:
            missing.append(i)

        if "expected_section" not in item:
            missing.append(i)

    if missing:

        print(
            f"WARNING: Missing fields in queries: "
            f"{sorted(set(missing))}"
        )

    else:

        print("Dataset validation: PASSED")

    print("=" * 70)


if __name__ == "__main__":
    validate_dataset()