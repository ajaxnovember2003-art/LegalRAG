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
        "causes the death of another",
        "causes death",
        "intention to cause death",
        "intending to cause death",
        "intentional killing",
        "kills another person",
    ],

    "culpable homicide": [
        "culpable homicide",
        "causes death",
        "knowledge likely to cause death",
        "knowledge that the act is likely to cause death",
        "intention of causing death",
        "intention to cause death",
        "act likely to cause death",
    ],

    "attempt to murder": [
        "attempt to murder",
        "attempts to cause death",
        "attempt to cause death",
        "attempting to cause death",
        "act towards causing death",
        "act towards commission",
        "direct step towards causing death",
        "death does not occur",
        "victim survives",
        "survives",
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
    ],

    "rape": [
        "rape",
        "sexual intercourse",
        "without consent",
        "without the consent",
        "sexual intercourse without consent",
        "against consent",
        "sexual act without consent",
    ],

    "sexual harassment": [
        "sexual harassment",
        "sexual remarks",
        "unwelcome sexual behaviour",
        "unwelcome sexual behavior",
        "unwelcome sexual conduct",
        "sexual remarks toward",
        "unwelcome sexual remarks",
    ],
}


# ============================================================
# QUERY OFFENCE DETECTION
# ============================================================

def detect_offence(query):

    q = query.lower()

    # --------------------------------------------------------
    # EXACT OFFENCE NAME HAS HIGHEST PRIORITY
    # --------------------------------------------------------

    exact_matches = []

    for offence in OFFENCE_SECTIONS:

        if offence in q:

            exact_matches.append(
                offence
            )

    if exact_matches:

        return max(
            exact_matches,
            key=len
        )

    # --------------------------------------------------------
    # CONCEPT-BASED DETECTION
    # --------------------------------------------------------

    offence_scores = {}

    for offence, phrases in LEGAL_CONCEPTS.items():

        score = 0.0

        for phrase in phrases:

            phrase_lower = phrase.lower()

            if phrase_lower not in q:
                continue

            words = phrase_lower.split()

            # Longer phrases provide stronger evidence
            if len(words) >= 5:
                score += 0.50

            elif len(words) == 4:
                score += 0.40

            elif len(words) == 3:
                score += 0.25

            elif len(words) == 2:
                score += 0.15

            else:
                score += 0.05

        offence_scores[
            offence
        ] = score

    if not offence_scores:

        return None

    best_offence = max(
        offence_scores,
        key=offence_scores.get
    )

    best_score = offence_scores[
        best_offence
    ]

    if best_score < 0.25:

        return None

    return best_offence

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

    matched = 0

    for phrase in phrases:

        if phrase.lower() in text_lower:

            matched += 1

    return (
        matched /
        len(phrases)
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

    punishment = punishment_score(
        query,
        text
    )

    section = section_score(
        offence,
        metadata
    )

    # Existing dense / RRF score
    base_score = float(
        result.get(
            "score",
            0.0
        )
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # DO NOT LET LEGAL HEURISTICS OVERRIDE
    # STRONG RETRIEVAL COMPLETELY.
    # --------------------------------------------------------

    legal_boost = (

        section * 0.35

        +

        concept * 0.20

        +

        lexical * 0.10

        +

        punishment * 0.10

    )

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

    reranked = []

    for result in results:

        item = result.copy()

        legal_score = (
            calculate_legal_score(
                query,
                item
            )
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
    #
    # Avoid returning multiple chunks
    # from exactly the same section.
    # --------------------------------------------------------

    final = []

    seen_sections = set()

    for result in reranked:

        section = str(
            result.get(
                "metadata",
                {}
            ).get(
                "section",
                ""
            )
        ).strip()

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
            f"{i:02d}. Section "
            f"{metadata.get('section', '?')} "
            f"score={result['legal_score']:.6f}"
        )

    return final