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
        "causes death",
        "intention to cause death",
        "knowledge",
    ],

    "culpable homicide": [
        "culpable homicide",
        "causes death",
        "intention",
        "knowledge likely to cause death",
    ],

    "attempt to murder": [
        "attempt to murder",
        "attempt",
        "act towards commission",
        "death",
    ],

    "theft": [
        "theft",
        "dishonestly takes",
        "movable property",
        "possession",
        "without consent",
    ],

    "robbery": [
        "robbery",
        "theft",
        "extortion",
        "violence",
        "fear of instant hurt",
    ],

    "dacoity": [
        "dacoity",
        "five or more persons",
        "robbery",
    ],

    "extortion": [
        "extortion",
        "fear of injury",
        "delivery of property",
        "dishonestly induces",
    ],

    "criminal breach of trust": [
        "criminal breach of trust",
        "entrusted",
        "dominion over property",
        "dishonestly misappropriates",
        "dishonestly converts",
    ],

    "stolen property": [
        "stolen property",
        "stolen",
        "dishonestly receives",
        "retains",
    ],

    "receiving stolen property": [
        "receiving stolen property",
        "dishonestly receives",
        "retains stolen property",
        "knowing",
    ],

    "cheating": [
        "cheating",
        "deception",
        "dishonestly induces",
        "delivery of property",
    ],

    "wrongful restraint": [
        "wrongful restraint",
        "voluntarily obstructs",
        "preventing a person from proceeding",
    ],

    "wrongful confinement": [
        "wrongful confinement",
        "wrongfully confines",
        "confined within limits",
    ],

    "criminal intimidation": [
        "criminal intimidation",
        "threat",
        "injury",
        "reputation",
        "property",
    ],

    "rape": [
        "rape",
        "sexual intercourse",
        "without consent",
        "sexual assault",
    ],

    "sexual harassment": [
        "sexual harassment",
        "sexual remarks",
        "unwelcome sexual behaviour",
    ],
}


# ============================================================
# QUERY OFFENCE DETECTION
# ============================================================

def detect_offence(query):

    q = query.lower()

    offences = sorted(
        OFFENCE_SECTIONS.keys(),
        key=len,
        reverse=True
    )

    for offence in offences:

        if offence in q:

            return offence

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