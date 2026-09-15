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
          "fear of instant death",
          "fear of instant hurt",
          "fear of instant wrongful restraint",
          "instant death",
          "instant hurt",
          "instant wrongful restraint",
           "violence",
           "takes property",
          "taking property"
        ],
         "negative": [
           "entrusted with property",
        "dishonestly misappropriates",
             "dishonestly converts",
         "deception",
           "cause alarm"
         ]
    },

    "dacoity": {
        "positive": [
            "five or more persons",
            "five or more people",
            "five or more persons conjointly",
            "conjointly commit robbery",
            "conjointly commit or attempt",
            "persons present and aiding",
            "amount to five or more",
            "jointly commits robbery",
            "jointly commit robbery"
        ],
        "negative": [
            "single person",
            "two persons",
            "three persons",
            "four persons"
        ]
    },

    "extortion": {
        "positive": [
            "puts or attempts to put any person in fear",
            "puts any person in fear",
            "fear of injury",
            "fear of harm",
            "deliver any property",
            "delivery of property",
            "delivery of money",
            "dishonestly induces",
            "putting a person in fear"
        ],
        "negative": [
            "takes movable property",
            "moves property",
            "entrusted with property",
            "dishonestly misappropriates",
            "dishonestly converts",
            "cause alarm"
        ]
    },

    "criminal breach of trust": {
        "positive": [
            "entrusted with property",
            "entrusted with money",
            "entrusted with dominion",
            "dominion over property",
            "dishonestly misappropriates",
            "dishonestly misappropriated",
            "dishonestly converts",
            "dishonestly converted",
            "converts to his own use",
            "uses or disposes",
            "in violation of any direction of law",
            "in violation of any legal contract",
            "discharge of such trust"
        ],
        "negative": [
            "deception",
            "fear of injury",
            "fear of harm",
            "cause alarm",
            "threatens another"
        ]
    },

    "criminal intimidation": {
        "positive": [
            "threatens another with injury",
            "threat of injury",
            "threatens with injury",
            "threatens with harm",
            "intent to cause alarm",
            "cause alarm to that person",
            "cause alarm",
            "threatens another",
            "threatening another"
        ],
        "negative": [
            "fear of instant death",
            "fear of instant hurt",
            "fear of instant wrongful restraint",
            "five or more persons",
            "conjointly commit robbery",
            "deliver any property",
            "delivery of property",
            "entrusted with property",
            "dishonestly misappropriates",
            "dishonestly converts"
        ]
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
# STATUTORY ANCHORS
# ============================================================
# Highly distinctive phrases taken from the statutory language
# of important BNS provisions.
#
# These are intentionally stronger signals than generic
# legal concepts because they identify provision-specific
# wording.
# ============================================================

STATUTORY_ANCHORS = {

    # --------------------------------------------------------
    # SECTION 103 — MURDER
    # --------------------------------------------------------
    "murder": [
        "whoever commits murder shall be punished",
        "punished with death or imprisonment for life",
        "imprisonment for life",
        "and shall also be liable to fine",
    ],

    # --------------------------------------------------------
    # SECTION 105 — CULPABLE HOMICIDE
    # --------------------------------------------------------
    "culpable homicide": [
        "culpable homicide not amounting to murder",
        "intention of causing death",
        "knowledge that he is likely by such act to cause death",
        "knowledge that the act is likely to cause death",
    ],

    # --------------------------------------------------------
    # SECTION 109 — ATTEMPT TO MURDER
    # --------------------------------------------------------
    "attempt to murder": [
        "intention or knowledge",
        "if by that act he caused death",
        "would be guilty of murder",
        "does any act with such intention or knowledge",
    ],

    # --------------------------------------------------------
    # SECTION 310 — DACOITY
    # --------------------------------------------------------
    "dacoity": [
        "five or more persons conjointly",
        "conjointly commit or attempt",
        "persons present and aiding",
        "amount to five or more",
        "five or more persons",
    ],

    # --------------------------------------------------------
    # SECTION 308 — EXTORTION
    # --------------------------------------------------------
    "extortion": [
        "puts or attempts to put any person in fear",
        "fear of injury",
        "deliver to any person any property",
        "deliver any property",
        "valuable security",
    ],

    # --------------------------------------------------------
    # SECTION 316 — CRIMINAL BREACH OF TRUST
    # --------------------------------------------------------
    "criminal breach of trust": [
        "entrusted with property",
        "entrusted with money",
        "dominion over property",
        "dishonestly misappropriates",
        "dishonestly converts",
        "converts to his own use",
        "uses or disposes",
        "in violation of any direction of law",
        "in violation of any legal contract",
        "discharge of such trust",
    ],

    # --------------------------------------------------------
    # SECTION 317 — STOLEN PROPERTY
    # --------------------------------------------------------
    "stolen property": [
        "knowing or having reason to believe",
        "reason to believe it to be stolen",
        "property to be stolen",
        "receives or retains such property",
        "dishonestly receives",
        "dishonestly received",
    ],

    # --------------------------------------------------------
    # SECTION 318 — CHEATING
    # --------------------------------------------------------
    "cheating": [
        "deceiving any person",
        "fraudulently or dishonestly induces",
        "induces the person so deceived",
        "deliver any property",
        "retain any property",
    ],

    # --------------------------------------------------------
    # SECTION 303 — THEFT
    # --------------------------------------------------------
    "theft": [
        "dishonestly takes any movable property",
        "movable property",
        "out of the possession of any person",
        "without that person's consent",
        "moves that property",
    ],

    # --------------------------------------------------------
    # SECTION 309 — ROBBERY
    # --------------------------------------------------------
    "robbery": [
        "robbery or dacoity",
        "instant death",
        "instant hurt",
        "instant wrongful restraint",
        "fear of instant death",
        "fear of instant hurt",
        "fear of instant wrongful restraint",
    ],

    # --------------------------------------------------------
    # SECTION 126 — WRONGFUL RESTRAINT
    # --------------------------------------------------------
    "wrongful restraint": [
        "voluntarily obstructs a person",
        "from proceeding in any direction",
        "right to proceed",
        "prevented from proceeding",
    ],

    # --------------------------------------------------------
    # SECTION 127 — WRONGFUL CONFINEMENT
    # --------------------------------------------------------
    "wrongful confinement": [
        "wrongfully to confine",
        "circumscribing limits",
        "circumscribed limits",
        "proceeding beyond certain circumscribing limits",
        "prevented from proceeding beyond certain limits",
    ],

    # --------------------------------------------------------
    # SECTION 351 — CRIMINAL INTIMIDATION
    # --------------------------------------------------------
    "criminal intimidation": [
        "threatens another with injury",
        "threat of injury",
        "person, reputation or property",
        "intent to cause alarm",
        "cause alarm to that person",
    ],

    # --------------------------------------------------------
    # SECTION 64 — RAPE
    # --------------------------------------------------------
    "rape": [
        "sexual intercourse with a woman",
        "against her will",
        "without her consent",
        "with or without her consent",
    ],

    # --------------------------------------------------------
    # SECTION 75 — SEXUAL HARASSMENT
    # --------------------------------------------------------
    "sexual harassment": [
        "physical contact and advances involving unwelcome",
        "unwelcome and explicit sexual overtures",
        "demand or request for sexual favours",
        "showing pornography against the will",
        "sexually coloured remarks",
    ],
}

# ============================================================
# QUERY OFFENCE DETECTION
# ============================================================
def detect_offence(query):
    q = query.lower().strip()

    # ========================================================
    # 1. EXPLICIT HIGH-SPECIFICITY OFFENCES
    # ========================================================

    if "attempt to murder" in q:
        return "attempt to murder"

    if "culpable homicide" in q:
        return "culpable homicide"

    # ========================================================
    # 2. DACOITY — CHECK BEFORE ROBBERY
    # ========================================================

    dacoity_indicators = [
        "five or more persons",
        "five or more people",
        "five or more individuals",
        "five or more persons conjointly",
        "amount to five or more",
        "conjointly commit",
        "conjointly commit or attempt",
        "persons present and aiding",
        "five persons",
        "five people",
        "jointly commits robbery",
        "jointly commit robbery",
        "participate together in taking property",
    ]

    if any(
        phrase in q
        for phrase in dacoity_indicators
    ):
        return "dacoity"
    
    
    # ========================================================
    # 3. STOLEN PROPERTY    
    # ========================================================

    stolen_property_indicators = [
        "knowing that the property was stolen",
        "knowing the property was stolen",
        "knowing or having reason to believe",
        "knowing or having reasonable cause to believe",
        "having reason to believe",
        "having reasonable cause to believe",
        "reason to believe it to be stolen",
        "reason to believe the property was stolen",
        "property was unlawfully obtained",
        "property was unlawfully acquired",
        "unlawfully obtained property",
        "unlawfully obtained",
        "stolen property",
        "purchases and keeps property",
        "purchases and keeps the property",
        "purchases or receives",
        "receives or retains",
        "receives or retains such property",
        "retains such property",
        "dishonestly receives",
        "dishonestly received",
    ]

    if any(
        phrase in q
        for phrase in stolen_property_indicators
    ):
        return "stolen property"


    # ========================================================
    # 4. CRIMINAL BREACH OF TRUST
    # ========================================================

    trust_indicators = [
        "entrusted with property",
        "entrusted the property",
        "entrusted with money",
        "entrusted money",
        "position of trust",
        "under a position of trust",
        "dominion over property",
        "dominion over the property",
        "dishonestly misappropriates",
        "dishonestly misappropriated",
        "dishonestly converts",
        "dishonestly converted",
        "converts to his own use",
        "converted to his own use",
        "uses or disposes",
        "uses or disposes of that property",
        "discharge of such trust",
        "in violation of any direction of law",
        "in violation of any legal contract",
        "uses the property as their own",
        "uses the property as his own",
        "uses the property as her own",
    ]

    if any(
        phrase in q
        for phrase in trust_indicators
    ):
        return "criminal breach of trust"

    # ========================================================
    # 4. EXTORTION — FEAR + INDUCEMENT / DELIVERY
    # ========================================================

    extortion_property_indicators = [
        "deliver property",
        "delivery of property",
        "deliver money",
        "delivery of money",
        "hand over property",
        "hand over money",
        "hand over the property",
        "hand over the money",
        "dishonestly induces",
        "dishonestly induce",
        "induces them to hand over",
        "induces them to deliver",
        "induces a person to deliver",
        "induces the person so deceived",
        "valuable security",
    ]

    extortion_threat_indicators = [
        "threat",
        "threatens",
        "threatened",
        "threatening",
        "fear",
        "fear of injury",
        "fear of harm",
        "put in fear",
        "puts in fear",
        "immediate harm",
        "physical harm",
    ]

    if (
        any(
            phrase in q
            for phrase in extortion_property_indicators
        )
        and any(
            phrase in q
            for phrase in extortion_threat_indicators
        )
    ):
        return "extortion"

    # ========================================================
    # 5. ROBBERY — PROPERTY TAKING + VIOLENCE / IMMEDIATE FEAR
    # ========================================================

    robbery_property_indicators = [
        "takes property",
        "taking property",
        "takes the property",
        "property is taken",
        "property from another",
        "property from a victim",
        "taking property through robbery",
    ]

    robbery_force_indicators = [
        "violence",
        "fear of immediate harm",
        "fear of instant harm",
        "immediate physical harm",
        "instant hurt",
        "instant death",
        "fear of instant hurt",
        "fear of instant death",
        "wrongful restraint",
    ]

    if (
        any(
            phrase in q
            for phrase in robbery_property_indicators
        )
        and any(
            phrase in q
            for phrase in robbery_force_indicators
        )
    ):
        return "robbery"

    # ========================================================
    # 6. EXPLICIT OFFENCE NAMES
    # ========================================================

    explicit_offences = sorted(
        OFFENCE_SECTIONS.keys(),
        key=len,
        reverse=True
    )

    for offence in explicit_offences:
        if offence in q:
            return offence

    # ========================================================
    # 7. SEXUAL HARASSMENT
    # ========================================================

    sexual_harassment_indicators = [
        "physical contact and advances",
        "unwelcome and explicit sexual overtures",
        "demand or request for sexual favours",
        "showing pornography against the will",
        "sexually coloured remarks",
        "sexually coloured remark",
    ]

    if any(
        phrase in q
        for phrase in sexual_harassment_indicators
    ):
        return "sexual harassment"

    # ========================================================
    # 8. ATTEMPT TO MURDER
    # ========================================================

    attempt_indicators = [
        "death does not occur",
        "the victim survives",
        "victim survives",
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
    # 9. CULPABLE HOMICIDE
    # ========================================================

    culpable_homicide_indicators = [
        "knowledge likely to cause death",
        "knowledge that the act is likely to cause death",
        "knowing that the act is likely to cause death",
        "act likely to cause death",
        "likely to cause death",
        "without intention to cause death",
        "without intending to cause death",
        "without intent to cause death",
        "without intention of causing death",
        "not amounting to murder",
        "does not amount to murder",
        "knowledge that he is likely by such act to cause death",
    ]

    if any(
        phrase in q
        for phrase in culpable_homicide_indicators
    ):
        return "culpable homicide"

    # ========================================================
    # 10. MURDER
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
    # 11. HIGH-SPECIFICITY CONCEPT MATCHING
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

    matched_phrases = [
        phrase
        for phrase in phrases
        if phrase.lower() in text_lower
    ]

    if not matched_phrases:
        return 0.0

    # Strong evidence from multiple matching legal concepts.
    # The score saturates once sufficient evidence is present.
    return min(
        len(matched_phrases) / 3.0,
        1.0
    )

# ============================================================
# STATUTORY ANCHOR SCORE
# ============================================================

def statutory_anchor_score(offence, text):
    """
    Measures how strongly a retrieved passage matches
    provision-specific statutory language.

    The score saturates at 1.0 after three matched anchors,
    keeping it comparable with concept_score() and
    distinction_score().
    """

    if not offence:
        return 0.0

    text_lower = text.lower()

    anchors = STATUTORY_ANCHORS.get(
        offence,
        []
    )

    if not anchors:
        return 0.0

    matched_anchors = [
        phrase
        for phrase in anchors
        if phrase.lower() in text_lower
    ]

    if not matched_anchors:
        return 0.0

    return min(
        len(matched_anchors) / 3.0,
        1.0
    )

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

    positive_matches = [
        phrase
        for phrase in positive
        if phrase.lower() in text_lower
    ]

    negative_matches = [
        phrase
        for phrase in negative
        if phrase.lower() in text_lower
    ]

    # Positive evidence saturates at 3 matched phrases.
    positive_score = min(
        len(positive_matches) / 3.0,
        1.0
    )

    # Negative evidence also saturates.
    negative_score = min(
        len(negative_matches) / 3.0,
        1.0
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
    result,
    use_section_prior=True
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
    
    statutory_anchor = statutory_anchor_score(
        offence,
        text
    )
    

    punishment = punishment_score(
        query,
        text
    )

    if use_section_prior:
        section = section_score(
            offence,
            metadata
        )
    else:
        section = 0.0

    base_score = float(
        result.get(
            "score",
            result.get(
                "rrf_score",
                0.0
            )
        )
    )

    section_boost = (
        section * 0.60
    )

    distinction_boost = (
        distinction * 0.25
    )

    concept_boost = (
        concept * 0.15
    )

    statutory_anchor_boost = (
        statutory_anchor * 0.00
    )

    lexical_boost = (
        lexical * 0.05
    )

    punishment_boost = (
        punishment * 0.05
    )

    legal_boost = (
        section_boost
        + distinction_boost
        + concept_boost
        + statutory_anchor_boost
        + lexical_boost
        + punishment_boost
    )

    final_score = (
        base_score
        + legal_boost
    )

    # --------------------------------------------------------
    # DIAGNOSTIC COMPONENTS
    # --------------------------------------------------------

    result["score_components"] = {
        "base": base_score,      
        "section": section,
        "distinction": distinction,
        "concept": concept,
        "statutory_anchor": statutory_anchor,
        "lexical": lexical,
        "punishment": punishment,
        "section_boost": section_boost,
        "distinction_boost": distinction_boost,
        "concept_boost": concept_boost,
        "statutory_anchor_boost": statutory_anchor_boost,
        "lexical_boost": lexical_boost,
        "punishment_boost": punishment_boost,
        "legal_boost": legal_boost,
    }
    
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

# ============================================================
# LEGALRAG RERANKER
# ============================================================

def rerank_results(
    query,
    results,
    top_k=5,
    use_section_prior=True
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

    print(
        f"Section prior enabled: {use_section_prior}"
    )

    reranked = []

    for result in results:

        item = result.copy()

        legal_score = calculate_legal_score(
            query,
            item,
            use_section_prior=use_section_prior
        )

        components = item.get(
            "score_components",
            {}
        )

        item["legal_score"] = legal_score

        metadata = item.get(
            "metadata",
            {}
        )

        section = str(
            metadata.get(
                "section",
                ""
            )
        ).strip()

        # ----------------------------------------------------
        # EXTRACT MATCHED LEGAL EVIDENCE
        # ----------------------------------------------------

        text = item.get(
            "text",
            ""
        ).lower()

        matched_concepts = []

        if offence:

            for phrase in LEGAL_CONCEPTS.get(
                offence,
                []
            ):

                if phrase.lower() in text:

                    matched_concepts.append(
                        phrase
                    )

        matched_positive = []
        matched_negative = []

        if offence:

            rules = LEGAL_DISTINCTIONS.get(
                offence,
                {}
            )

            for phrase in rules.get(
                "positive",
                []
            ):

                if phrase.lower() in text:

                    matched_positive.append(
                        phrase
                    )

            for phrase in rules.get(
                "negative",
                []
            ):

                if phrase.lower() in text:

                    matched_negative.append(
                        phrase
                    )

        # ----------------------------------------------------
        # STORE DETAILED DIAGNOSTICS
        # ----------------------------------------------------

        item["legal_diagnostics"] = {

            "query_offence": offence,

            "section": section,

            "base_score": components.get(
                "base",
                0.0
            ),

            "section_score": components.get(
                "section",
                0.0
            ),

            "distinction_score": components.get(
                "distinction",
                0.0
            ),

            "concept_score": components.get(
                "concept",
                0.0
            ),
            
            

            "lexical_score": components.get(
                "lexical",
                0.0
            ),

            "punishment_score": components.get(
                "punishment",
                0.0
            ),

            "section_boost": components.get(
                "section_boost",
                0.0
            ),

            "distinction_boost": components.get(
                "distinction_boost",
                0.0
            ),

            "concept_boost": components.get(
                "concept_boost",
                0.0
            ),

            "lexical_boost": components.get(
                "lexical_boost",
                0.0
            ),

            "punishment_boost": components.get(
                "punishment_boost",
                0.0
            ),

            "legal_boost": components.get(
                "legal_boost",
                0.0
            ),

            "final_score": components.get(
                "final",
                legal_score
            ),

            "matched_concepts": matched_concepts,

            "matched_positive_phrases": matched_positive,

            "matched_negative_phrases": matched_negative
        }

        # ----------------------------------------------------
        # DETAILED CONSOLE DIAGNOSTIC
        # ----------------------------------------------------

        print(
            "\n--- LEGAL RERANK DIAGNOSTIC ---"
        )

        print(
            f"Section: {section}"
        )
        
        print(
            f"Base RRF: "
            f"{components.get('base', 0.0):.6f}"
            )
        
        print(
            f"Section score: "
            f"{components.get('section', 0.0):.6f}"
        )
        
        print(
            f"Distinction score: "
            f"{components.get('distinction', 0.0):.6f}"
        )
        
        print(
            f"Concept score: "
            f"{components.get('concept', 0.0):.6f}"
        )
        
        print(
            f"Statutory anchor score:"
            f"{components.get('statutory_anchor', 0.0):.6f}"
            )
        
        print(
            f"Lexical score: "
            f"{components.get('lexical', 0.0):.6f}"
            )
        
        print(
            f"Punishment score: "
            f"{components.get('punishment', 0.0):.6f}"
            )
        
        print(
            f"Section boost: "
            f"{components.get('section_boost', 0.0):.6f}"
            )
        
        print(
            f"Distinction boost: "
            f"{components.get('distinction_boost', 0.0):.6f}"
            )
        
        print(
            f"Concept boost: "
            f"{components.get('concept_boost', 0.0):.6f}"
            )
        
        print(
            f"Statutory anchor boost:"
            f"{components.get('statutory_anchor_boost', 0.0):.6f}"
            )
        
        print(
            f"Lexical boost: "
            f"{components.get('lexical_boost', 0.0):.6f}"
            )
        
        print(
            f"Punishment boost: "
            f"{components.get('punishment_boost', 0.0):.6f}"
            )
        
        print(
            f"LEGAL BOOST: "
            f"{components.get('legal_boost', 0.0):.6f}"
            )
        
        print(
            f"FINAL SCORE: "
            f"{components.get('final', legal_score):.6f}"
            )

        print(
            "Matched concepts:"
        )

        if matched_concepts:

            for phrase in matched_concepts:

                print(
                    f"  + {phrase}"
                )

        else:

            print(
                "  None"
            )

        print(
            "Matched positive distinction phrases:"
        )

        if matched_positive:

            for phrase in matched_positive:

                print(
                    f"  + {phrase}"
                )

        else:

            print(
                "  None"
            )

        print(
            "Matched negative distinction phrases:"
        )

        if matched_negative:

            for phrase in matched_negative:

                print(
                    f"  - {phrase}"
                )

        else:

            print(
                "  None"
            )

        reranked.append(
            item
        )

    # --------------------------------------------------------
    # SORT BY LEGAL SCORE
    # --------------------------------------------------------

    reranked.sort(
        key=lambda x:
        x["legal_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # DEDUPLICATE BY SECTION
    # --------------------------------------------------------

    final = []

    seen_sections = set()

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
    # FALLBACK IF FEWER THAN TOP_K UNIQUE SECTIONS
    # --------------------------------------------------------

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
    # FINAL RANKING DISPLAY
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

        diagnostics = result.get(
            "legal_diagnostics",
            {}
        )

        print(
            f"{i:02d}. "
            f"Section {metadata.get('section', '?')} "
            f"score={result['legal_score']:.6f} "
            f"section_score="
            f"{diagnostics.get('section_score', 0.0):.3f} "
            f"distinction="
            f"{diagnostics.get('distinction_score', 0.0):.3f} "
            f"concept="
            f"{diagnostics.get('concept_score', 0.0):.3f}"
        )

    return final