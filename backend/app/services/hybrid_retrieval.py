import re
import math


# ============================================================
# LEGAL SECTION MAP
# ============================================================

OFFENCE_SECTIONS = {

    "murder": "103",

    "culpable homicide": "105",

    "attempt to murder": "109",

    "theft": "303",

    "robbery": "309",

    "dacoity": "310",

    "extortion": "308",

    "criminal breach of trust": "316",

    "stolen property": "317",

    "receiving stolen property": "317",

    "cheating": "318",

    "wrongful restraint": "126",

    "wrongful confinement": "127",

    "criminal intimidation": "351",

    "rape": "64",

    "sexual harassment": "75",
}


# ============================================================
# LEGAL CONCEPT PHRASES
# ============================================================

LEGAL_CONCEPTS = {

    "murder": [
        "murder",
        "intentionally causes death",
        "intentionally causes the death",
        "causes the death of another",
        "causes death",
        "intention to cause death",
        "intending to cause death",
        "intentional killing",
        "kills another person",
        "causes another person's death",
    ],

    "culpable homicide": [
        "culpable homicide",
        "causes death",
        "causes another person's death",
        "knowledge likely to cause death",
        "knowledge that the act is likely to cause death",
        "intention of causing death",
        "intention to cause death",
        "act likely to cause death",
        "act that causes death",
        "required intention or knowledge",
        "intention or knowledge regarding the likelihood of death",
        "knowledge regarding the likelihood of death",
    ],

    "attempt to murder": [
        "attempt to murder",
        "attempts to cause death",
        "attempt to cause death",
        "attempting to cause death",
        "act towards causing death",
        "act toward causing death",
        "direct step towards causing death",
        "direct step toward causing death",
        "death does not occur",
        "victim survives",
        "the victim survives",
        "but death does not occur",
        "towards causing another person's death",
        "toward causing another person's death",
    ],

    "theft": [
        "theft",
        "dishonestly takes",
        "dishonestly taking",
        "movable property",
        "moves property",
        "possession",
        "without consent",
    ],

    "robbery": [
        "robbery",
        "theft",
        "extortion",
        "violence",
        "fear of instant hurt",
        "instant hurt",
        "instant death",
    ],

    "dacoity": [
        "dacoity",
        "five or more persons",
        "five or more",
        "robbery",
        "jointly commit robbery",
    ],

    "extortion": [
        "extortion",
        "fear of injury",
        "fear of harm",
        "delivery of property",
        "dishonestly induces",
        "induces another person",
        "putting a person in fear",
    ],

    "criminal breach of trust": [
        "criminal breach of trust",
        "entrusted",
        "entrusted with property",
        "entrusted with dominion",
        "dominion over property",
        "dishonestly misappropriates",
        "dishonestly converts",
        "misappropriates property",
    ],

    "stolen property": [
        "stolen property",
        "stolen",
        "dishonestly receives",
        "dishonestly receiving",
        "retains stolen property",
        "retains property",
        "knowing it to be stolen",
    ],

    "receiving stolen property": [
        "receiving stolen property",
        "dishonestly receives",
        "dishonestly receiving",
        "retains stolen property",
        "knowing it to be stolen",
    ],

    "cheating": [
        "cheating",
        "deception",
        "deceives",
        "deception of another person",
        "dishonestly induces",
        "dishonestly inducing",
        "delivery of property",
        "induces a person to deliver property",
        "transfer property",
        "transfers property",
        "cause another person to transfer property",
        "deception to cause transfer",
    ],

    "wrongful restraint": [
        "wrongful restraint",
        "voluntarily obstructs",
        "voluntarily obstruct",
        "prevents a person from proceeding",
        "preventing a person from proceeding",
        "cannot proceed",
        "right to proceed",
    ],

    "wrongful confinement": [
        "wrongful confinement",
        "wrongfully confines",
        "confined within limits",
        "prevents a person from leaving",
        "prevents another from leaving",
        "restricted area",
        "moving beyond certain limits",
        "prevents a person from moving",
    ],

    "criminal intimidation": [
        "criminal intimidation",
        "threat",
        "threatens",
        "threatening",
        "injury",
        "harm",
        "reputation",
        "property",
        "cause alarm",
        "cause fear",
        "intention of causing fear",
        "in order to cause alarm",
    ],

    "rape": [
        "rape",
        "sexual intercourse",
        "without consent",
        "without the consent",
        "sexual intercourse without consent",
        "against consent",
        "sexual act without consent",
        "engages in sexual intercourse",
        "sexual intercourse with another person",
    ],

    "sexual harassment": [
        "sexual harassment",
        "sexual remarks",
        "unwelcome sexual behaviour",
        "unwelcome sexual behavior",
        "unwelcome sexual conduct",
        "sexual remarks toward",
        "unwelcome sexual remarks",
        "unwelcome sexual behaviour toward",
        "unwelcome sexual behavior toward",
        "sexual remarks or",
    ],
}

# ============================================================
# LEGAL DISTINCTIONS
# ============================================================

LEGAL_DISTINCTIONS = {

    "murder": {
        "positive": [
            "intention to cause death",
            "intentionally causes death",
            "intending to cause death",
            "intentional killing",
        ],
        "negative": [
            "death does not occur",
            "victim survives",
            "attempt to murder",
            "knowledge likely to cause death",
        ],
    },

    "culpable homicide": {
        "positive": [
            "knowledge likely to cause death",
            "knowledge that the act is likely to cause death",
            "act likely to cause death",
            "causes death",
        ],
        "negative": [
            "death does not occur",
            "victim survives",
            "attempt to murder",
            "intention to cause death",
        ],
    },

    "attempt to murder": {
        "positive": [
            "attempt to cause death",
            "attempting to cause death",
            "act towards causing death",
            "death does not occur",
            "victim survives",
        ],
        "negative": [
            "causes death",
            "death occurs",
        ],
    },

    "theft": {
        "positive": [
            "dishonestly takes",
            "movable property",
            "moves property",
            "without consent",
        ],
        "negative": [
            "fear of injury",
            "delivery of property",
            "entrusted with property",
            "deception",
        ],
    },

    "robbery": {
        "positive": [
            "fear of instant hurt",
            "instant hurt",
            "instant death",
            "violence",
            "theft",
            "extortion",
        ],
        "negative": [
            "five or more persons",
            "entrusted with property",
            "deception",
        ],
    },

    "dacoity": {
        "positive": [
            "five or more persons",
            "five or more",
            "jointly commit robbery",
            "robbery",
        ],
        "negative": [
            "single person",
            "two persons",
        ],
    },

    "extortion": {
        "positive": [
            "fear of injury",
            "fear of harm",
            "delivery of property",
            "dishonestly induces",
            "putting a person in fear",
        ],
        "negative": [
            "takes movable property",
            "without consent",
            "entrusted with property",
        ],
    },

    "criminal breach of trust": {
        "positive": [
            "entrusted",
            "entrusted with property",
            "entrusted with dominion",
            "dominion over property",
            "dishonestly misappropriates",
            "dishonestly converts",
        ],
        "negative": [
            "deception",
            "induces a person to deliver property",
            "fear of injury",
        ],
    },

    "stolen property": {
        "positive": [
            "stolen property",
            "dishonestly receives",
            "retains stolen property",
            "knowing it to be stolen",
        ],
        "negative": [
            "entrusted with property",
            "deception",
            "fear of injury",
        ],
    },

    "receiving stolen property": {
        "positive": [
            "dishonestly receives",
            "dishonestly receiving",
            "retains stolen property",
            "knowing it to be stolen",
        ],
        "negative": [
            "deception",
            "entrusted with property",
        ],
    },

    "cheating": {
        "positive": [
            "deception",
            "deceives",
            "dishonestly induces",
            "dishonestly inducing",
            "delivery of property",
            "induces a person to deliver property",
            "transfer property",
        ],
        "negative": [
            "fear of injury",
            "entrusted with property",
            "stolen property",
        ],
    },

    "wrongful restraint": {
        "positive": [
            "voluntarily obstructs",
            "voluntarily obstruct",
            "prevents a person from proceeding",
            "cannot proceed",
            "right to proceed",
        ],
        "negative": [
            "prevents a person from leaving",
            "confined within limits",
            "restricted area",
        ],
    },

    "wrongful confinement": {
        "positive": [
            "wrongfully confines",
            "confined within limits",
            "prevents a person from leaving",
            "restricted area",
            "moving beyond certain limits",
        ],
        "negative": [
            "cannot proceed",
            "right to proceed",
            "voluntarily obstructs",
        ],
    },

    "criminal intimidation": {
        "positive": [
            "threatens",
            "threat",
            "injury",
            "harm",
            "reputation",
            "property",
            "cause alarm",
            "cause fear",
        ],
        "negative": [
            "sexual remarks",
            "sexual behaviour",
            "sexual behavior",
            "sexual intercourse",
        ],
    },

    "rape": {
        "positive": [
            "sexual intercourse",
            "without consent",
            "without the consent",
            "against consent",
            "sexual act without consent",
        ],
        "negative": [
            "sexual remarks",
            "sexual harassment",
            "unwelcome sexual behaviour",
            "unwelcome sexual behavior",
        ],
    },

    "sexual harassment": {
        "positive": [
            "sexual remarks",
            "unwelcome sexual behaviour",
            "unwelcome sexual behavior",
            "unwelcome sexual conduct",
            "sexual remarks toward",
            "unwelcome sexual remarks",
        ],
        "negative": [
            "sexual intercourse",
            "without consent",
            "causes death",
        ],
    },
}

# ============================================================
# QUERY OFFENCE DETECTION
# ============================================================
def detect_offence(query):

    q = query.lower().strip()

    # ========================================================
    # 1. EXPLICIT OFFENCE NAMES — HIGHEST PRIORITY
    # ========================================================

    # Attempt to murder must come first because it contains
    # the word "murder".
    if "attempt to murder" in q:
        return "attempt to murder"

    # Explicit murder
    if re.search(r"\bmurder\b", q):
        return "murder"

    # Explicit culpable homicide
    if "culpable homicide" in q:
        return "culpable homicide"

    # Other explicit offence names
    explicit_offences = sorted(
        OFFENCE_SECTIONS.keys(),
        key=len,
        reverse=True
    )

    for offence in explicit_offences:
        if offence in q:
            return offence

    # ========================================================
    # 2. ATTEMPT-TO-MURDER CONCEPTS
    # ========================================================

    attempt_indicators = [
        "death does not occur",
        "victim survives",
        "the victim survives",
        "attempting to cause death",
        "attempt to cause death",
        "attempts to cause death",
        "direct step towards causing death",
        "direct step toward causing death",
        "tries to kill",
        "tried to kill",
        "attempted killing",
    ]

    if any(
        phrase in q
        for phrase in attempt_indicators
    ):
        return "attempt to murder"

    # ========================================================
    # 3. MURDER CONCEPTS
    # ========================================================

    murder_indicators = [
        "intention to cause death",
        "intention of causing death",
        "intending to cause death",
        "intentionally causes death",
        "intentionally causes the death",
        "intentionally causing death",
        "intentional killing",
        "intends to kill",
        "intended to kill",
        "intention to kill",
        "intention of killing",
        "intent to cause death",
        "intent of causing death",
        "causes death with the intention",
        "causes the death with the intention",
        "caused death with the intention",
        "caused the death with the intention",
    ]

    if any(
        phrase in q
        for phrase in murder_indicators
    ):
        return "murder"

    # ========================================================
    # 4. CULPABLE HOMICIDE CONCEPTS
    # ========================================================

    culpable_homicide_indicators = [
        "knowledge likely to cause death",
        "knowledge that the act is likely to cause death",
        "knowing that the act is likely to cause death",
        "act likely to cause death",
        "without intention to cause death",
        "without intending to cause death",
        "without intent to cause death",
        "without intention of causing death",
    ]

    if any(
        phrase in q
        for phrase in culpable_homicide_indicators
    ):
        return "culpable homicide"

    # ========================================================
    # 5. OTHER CONCEPT-BASED DETECTION
    # ========================================================

    concept_matches = {}

    for offence, phrases in LEGAL_CONCEPTS.items():

        matches = sum(
            1
            for phrase in phrases
            if phrase.lower() in q
        )

        if matches > 0:
            concept_matches[offence] = matches

    if concept_matches:
        return max(
            concept_matches,
            key=concept_matches.get
        )

    # ========================================================
    # 6. NO OFFENCE DETECTED
    # ========================================================

    return None

# ============================================================
# QUERY INTENT
# ============================================================

def detect_intent(query):

    q = query.lower()

    if any(
        word in q
        for word in [
            "punishment",
            "punishable",
            "penalty",
            "sentence",
            "imprisonment",
            "fine",
        ]
    ):

        return "punishment"

    if any(
        phrase in q
        for phrase in [
            "what is",
            "define",
            "definition",
            "meaning",
            "explain",
        ]
    ):

        return "definition"

    return "general"


# ============================================================
# TOKENIZE
# ============================================================

def tokenize(text):

    return set(
        re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )
    )


# ============================================================
# TEXT SIMILARITY
# ============================================================

def lexical_similarity(
    query,
    text
):

    q_tokens = tokenize(
        query
    )

    t_tokens = tokenize(
        text
    )

    if not q_tokens:

        return 0.0

    intersection = (
        q_tokens &
        t_tokens
    )

    return (
        len(intersection)
        /
        len(q_tokens)
    )


# ============================================================
# LEGAL CONCEPT SCORE
# ============================================================

def concept_score(
    offence,
    text
):

    if not offence:
        return 0.0

    text_lower = text.lower()

    phrases = LEGAL_CONCEPTS.get(
        offence,
        []
    )

    if not phrases:
        return 0.0

    matched = sum(
        1
        for phrase in phrases
        if phrase.lower() in text_lower
    )

    return matched / len(phrases)

# ============================================================
# LEGAL DISTINCTION SCORE
# ============================================================

def distinction_score(
    offence,
    text
):

    if not offence:
        return 0.0

    text_lower = text.lower()

    rules = LEGAL_DISTINCTIONS.get(
        offence
    )

    if not rules:
        return 0.0

    positive = rules.get(
        "positive",
        []
    )

    negative = rules.get(
        "negative",
        []
    )

    positive_matches = sum(
        1
        for phrase in positive
        if phrase.lower() in text_lower
    )

    negative_matches = sum(
        1
        for phrase in negative
        if phrase.lower() in text_lower
    )

    positive_score = (
        positive_matches /
        max(len(positive), 1)
    )

    negative_score = (
        negative_matches /
        max(len(negative), 1)
    )

    return max(
        positive_score -
        (negative_score * 0.75),
        0.0
    )

# ============================================================
# PUNISHMENT SCORE
# ============================================================

def punishment_score(
    query,
    text
):

    intent = detect_intent(
        query
    )

    if intent != "punishment":

        return 0.0

    text_lower = text.lower()

    terms = [
        "punishment",
        "punishable",
        "imprisonment",
        "fine",
        "penalty",
        "shall be punished",
        "term",
    ]

    matches = sum(
        1
        for term in terms
        if term in text_lower
    )

    return min(
        matches / 3.0,
        1.0
    )


# ============================================================
# SECTION SCORE
# ============================================================

def section_score(
    offence,
    metadata
):

    if not offence:

        return 0.0

    expected_section = (
        OFFENCE_SECTIONS.get(
            offence
        )
    )

    actual_section = str(
        metadata.get(
            "section",
            ""
        )
    ).strip()

    if (
        expected_section
        and actual_section
        == expected_section
    ):

        return 1.0

    return 0.0


# ============================================================
# LEGAL RERANK SCORE
# ============================================================

def calculate_legal_score(
    query,
    result
):

    text = result.get(
        "text",
        ""
    )

    metadata = result.get(
        "metadata",
        {}
    )

    offence = detect_offence(
        query
    )

    # --------------------------------------------------------
    # COMPONENTS
    # --------------------------------------------------------

    lexical = lexical_similarity(
        query,
        text
    )

    concept = concept_score(
        offence,
        text
    )

    distinction = distinction_score(
        offence,
        text
    )

    punishment = punishment_score(
        query,
        text
    )

    section = section_score(
        offence,
        metadata
    )

    # --------------------------------------------------------
    # BASE RETRIEVAL SCORE
    # --------------------------------------------------------

    base_score = float(
        result.get(
            "score",
            result.get(
                "rrf_score",
                0.0
            )
        )
    )

    # --------------------------------------------------------
    # LEGAL BOOST
    # --------------------------------------------------------

    legal_boost = (

        section * 0.60

        +

        distinction * 0.25

        +

        concept * 0.15

        +

        lexical * 0.05

        +

        punishment * 0.05
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    final_score = (
        base_score
        +
        legal_boost
    )

    return final_score

# ============================================================
# RECIPROCAL RANK FUSION
# ============================================================

def reciprocal_rank_fusion(
    dense_results,
    bm25_results,
    rrf_k=60
):

    scores = {}

    objects = {}

    # --------------------------------------------------------
    # DENSE
    # --------------------------------------------------------

    for rank, result in enumerate(
        dense_results,
        start=1
    ):

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

        key = (
            metadata.get(
                "document",
                ""
            ),
            section,
            metadata.get(
                "source",
                ""
            ),
        )

        scores.setdefault(
            key,
            0.0
        )

        scores[key] += (
            1.0 /
            (rrf_k + rank)
        )

        objects[key] = result

    # --------------------------------------------------------
    # BM25
    # --------------------------------------------------------

    for rank, result in enumerate(
        bm25_results,
        start=1
    ):

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

        key = (
            metadata.get(
                "document",
                ""
            ),
            section,
            metadata.get(
                "source",
                ""
            ),
        )

        scores.setdefault(
            key,
            0.0
        )

        scores[key] += (
            1.0 /
            (rrf_k + rank)
        )

        if key not in objects:

            objects[key] = result

    # --------------------------------------------------------
    # CREATE RESULTS
    # --------------------------------------------------------

    results = []

    for key, rrf_score in scores.items():

        result = objects[key].copy()

        result[
            "rrf_score"
        ] = rrf_score

        result[
            "score"
        ] = rrf_score

        results.append(
            result
        )

    results.sort(
        key=lambda x: x[
            "rrf_score"
        ],
        reverse=True
    )

    return results


# ============================================================
# LEGALRAG RERANKER
# ============================================================

def rerank_results(
    query,
    results,
    top_k=5
):

    print(
        "\nLegalRAG reranking..."
    )

    offence = detect_offence(
        query
    )

    print(
        f"Detected offence: {offence}"
    )

    reranked = []

    for result in results:

        item = result.copy()

        legal_score = calculate_legal_score(
            query,
            item
        )

        item[
            "legal_score"
        ] = legal_score

        reranked.append(
            item
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    reranked.sort(
        key=lambda x:
        x["legal_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # SECTION DIVERSITY
    # --------------------------------------------------------

    final = []

    seen_sections = set()

    # First pass:
    # Prefer unique sections.

    for result in reranked:

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

        if not section:
            section = "UNKNOWN"

        if section in seen_sections:
            continue

        seen_sections.add(
            section
        )

        final.append(
            result
        )

        if len(final) >= top_k:
            break

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------
    # If diversity filtering produced fewer than top_k,
    # fill remaining positions.

    if len(final) < top_k:

        selected_ids = {
            id(result)
            for result in final
        }

        for result in reranked:

            if id(result) in selected_ids:
                continue

            final.append(
                result
            )

            if len(final) >= top_k:
                break

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print(
        "\nReranked sections:"
    )

    for i, result in enumerate(
        final,
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )

        print(
            f"{i:02d}. "
            f"Section {metadata.get('section', '?')} "
            f"score={result['legal_score']:.6f}"
        )

    return final