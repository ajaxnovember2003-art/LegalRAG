import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

INDEX_PATH = "data/vector_store/legal.index"
CHUNKS_PATH = "data/vector_store/chunks.pkl"

DEFAULT_K = 10


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading retrieval model...")

model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")

index = faiss.read_index(INDEX_PATH)

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)

print("FAISS Loaded!")
print("Total vectors:", index.ntotal)
print("Total chunks:", len(chunks))


# ============================================================
# LEGAL OFFENCE -> SECTION MAP
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
# LEGAL QUERY EXPANSIONS
# ============================================================

LEGAL_EXPANSIONS = {

    "murder": [
        "murder",
        "causes death",
        "intention to cause death",
        "murder punishment",
        "punishment for murder",
        "section 103",
    ],

    "culpable homicide": [
        "culpable homicide",
        "causes death",
        "intention of causing death",
        "knowledge likely to cause death",
        "culpable homicide punishment",
        "section 105",
    ],

    "attempt to murder": [
        "attempt to murder",
        "attempted murder",
        "act towards commission of murder",
        "intention or knowledge",
        "attempt to cause death",
        "section 109",
    ],

    "theft": [
        "theft",
        "dishonestly takes movable property",
        "movable property out of possession",
        "without consent",
        "dishonest intention",
        "theft punishment",
        "section 303",
    ],

    "robbery": [
        "robbery",
        "theft or extortion",
        "violence",
        "fear of instant hurt",
        "property",
        "robbery punishment",
        "section 309",
    ],

    "dacoity": [
        "dacoity",
        "five or more persons",
        "robbery by five or more persons",
        "jointly commit robbery",
        "dacoity punishment",
        "section 310",
    ],

    "extortion": [
        "extortion",
        "fear of injury",
        "dishonestly induces delivery of property",
        "putting person in fear",
        "property",
        "extortion punishment",
        "section 308",
    ],

    "criminal breach of trust": [
        "criminal breach of trust",
        "entrusted with property",
        "dominion over property",
        "dishonestly misappropriates",
        "dishonestly converts property",
        "criminal breach of trust punishment",
        "section 316",
    ],

    "stolen property": [
        "stolen property",
        "property stolen",
        "robbed property",
        "dishonestly receives stolen property",
        "retains stolen property",
        "section 317",
    ],

    "receiving stolen property": [
        "receiving stolen property",
        "dishonestly receiving stolen property",
        "retaining stolen property",
        "knowing or having reason to believe",
        "stolen property",
        "section 317",
    ],

    "cheating": [
        "cheating",
        "deception",
        "dishonestly induces",
        "delivery of property",
        "fraud",
        "cheating punishment",
        "section 318",
    ],

    "wrongful restraint": [
        "wrongful restraint",
        "voluntarily obstructs",
        "preventing a person from proceeding",
        "right to proceed",
        "section 126",
    ],

    "wrongful confinement": [
        "wrongful confinement",
        "wrongfully confines",
        "confined within limits",
        "preventing a person from proceeding",
        "section 127",
    ],

    "criminal intimidation": [
        "criminal intimidation",
        "threat",
        "threatens another person",
        "injury to person",
        "injury to reputation",
        "injury to property",
        "section 351",
    ],

    "rape": [
        "rape",
        "sexual intercourse",
        "sexual assault",
        "without consent",
        "section 64",
    ],

    "sexual harassment": [
        "sexual harassment",
        "unwelcome sexual behaviour",
        "sexual remarks",
        "section 75",
    ],
}


# ============================================================
# DETECT OFFENCE
# ============================================================

def detect_offence(query):
    """
    Detect the legal offence mentioned in the query.

    Uses longest-match-first so that:
        "criminal breach of trust"
    is detected before:
        "trust"
    """

    query_lower = query.lower()

    candidates = sorted(
        OFFENCE_SECTIONS.keys(),
        key=len,
        reverse=True
    )

    for offence in candidates:

        if offence in query_lower:

            return offence

    # Common aliases

    aliases = {

        "homicide": "culpable homicide",

        "attempted murder": "attempt to murder",

        "stolen goods": "stolen property",

        "wrongful confinement": "wrongful confinement",

        "intimidation": "criminal intimidation",

    }

    for alias, offence in aliases.items():

        if alias in query_lower:

            return offence

    return None


# ============================================================
# DETECT QUERY INTENT
# ============================================================

def detect_intent(query):

    q = query.lower()

    punishment_words = [
        "punishment",
        "penalty",
        "sentence",
        "imprisonment",
        "fine",
        "punishable",
        "punished",
    ]

    definition_words = [
        "what is",
        "define",
        "meaning",
        "definition",
        "explain",
    ]

    if any(word in q for word in punishment_words):

        return "punishment"

    if any(word in q for word in definition_words):

        return "definition"

    return "general"


# ============================================================
# GENERATE MULTIPLE RETRIEVAL QUERIES
# ============================================================

def generate_retrieval_queries(query):

    offence = detect_offence(query)

    intent = detect_intent(query)

    queries = []

    # --------------------------------------------------------
    # ORIGINAL QUERY
    # --------------------------------------------------------

    queries.append(query)

    # --------------------------------------------------------
    # OFFENCE
    # --------------------------------------------------------

    if offence:

        queries.append(offence)

    # --------------------------------------------------------
    # LEGAL EXPANSIONS
    # --------------------------------------------------------

    if offence in LEGAL_EXPANSIONS:

        queries.extend(
            LEGAL_EXPANSIONS[offence]
        )

    # --------------------------------------------------------
    # INTENT-SPECIFIC QUERIES
    # --------------------------------------------------------

    if offence:

        section = OFFENCE_SECTIONS.get(offence)

        if intent == "punishment":

            queries.extend([
                f"punishment for {offence}",
                f"penalty for {offence}",
                f"{offence} punishable",
                f"imprisonment for {offence}",
                f"fine for {offence}",
            ])

        elif intent == "definition":

            queries.extend([
                f"definition of {offence}",
                f"meaning of {offence}",
                f"what constitutes {offence}",
            ])

        if section:

            queries.append(
                f"section {section} {offence}"
            )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    queries = list(
        dict.fromkeys(
            q.strip()
            for q in queries
            if q and q.strip()
        )
    )

    return queries


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if not text:

        return ""

    return " ".join(
        str(text).lower().split()
    )


# ============================================================
# KEYWORD SCORE
# ============================================================

def keyword_score(
    query,
    text,
    metadata
):

    q = normalize_text(query)
    t = normalize_text(text)

    score = 0.0

    section = str(
        metadata.get(
            "section",
            ""
        )
    ).strip()

    offence = detect_offence(query)

    expected_section = (
        OFFENCE_SECTIONS.get(offence)
        if offence
        else None
    )

    # --------------------------------------------------------
    # SECTION MATCH
    # --------------------------------------------------------

    if expected_section:

        if section == expected_section:

            score += 12.0

    # --------------------------------------------------------
    # OFFENCE MATCH
    # --------------------------------------------------------

    if offence:

        if offence in t:

            score += 5.0

    # --------------------------------------------------------
    # PUNISHMENT TERMS
    # --------------------------------------------------------

    punishment_terms = [
        "punishment",
        "punishable",
        "imprisonment",
        "fine",
        "penalty",
        "sentence",
    ]

    if any(
        word in q
        for word in punishment_terms
    ):

        for word in punishment_terms:

            if word in t:

                score += 0.7

    # --------------------------------------------------------
    # LEGAL PHRASE MATCHING
    # --------------------------------------------------------

    important_phrases = {

        "murder": [
            "causes death",
            "intention",
            "knowledge",
        ],

        "culpable homicide": [
            "causes death",
            "intention",
            "knowledge",
        ],

        "attempt to murder": [
            "attempt",
            "murder",
            "death",
        ],

        "theft": [
            "dishonestly takes",
            "movable property",
            "possession",
        ],

        "criminal breach of trust": [
            "entrusted",
            "property",
            "misappropriates",
            "converts",
        ],

        "cheating": [
            "deception",
            "dishonestly induces",
            "property",
        ],

        "criminal intimidation": [
            "threat",
            "injury",
            "reputation",
        ],

    }

    if offence in important_phrases:

        for phrase in important_phrases[offence]:

            if phrase in t:

                score += 1.5

    return score


# ============================================================
# EXACT SECTION LOOKUP
# ============================================================

def get_exact_section_result(section):

    section = str(section).strip()

    for chunk in chunks:

        metadata = chunk.get(
            "metadata",
            {}
        )

        chunk_section = str(
            metadata.get(
                "section",
                ""
            )
        ).strip()

        if chunk_section == section:

            return {
                "text": chunk.get(
                    "text",
                    ""
                ),
                "metadata": metadata,
                "score": 0.0,
                "target_injected": False,
                "exact_section_match": True,
            }

    return None


# ============================================================
# SINGLE QUERY DENSE SEARCH
# ============================================================

def search_documents(
    query,
    k=10
):

    print("\n----------------------------------------")
    print("DENSE RETRIEVAL")
    print("----------------------------------------")

    print(
        "Query:",
        query
    )

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    retrieval_k = min(
        max(k * 5, 50),
        index.ntotal
    )

    distances, indices = index.search(
        query_embedding,
        retrieval_k
    )

    results = []

    seen = set()

    for idx, distance in zip(
        indices[0],
        distances[0]
    ):

        if idx < 0:

            continue

        if idx >= len(chunks):

            continue

        chunk = chunks[idx]

        metadata = chunk.get(
            "metadata",
            {}
        )

        section = str(
            metadata.get(
                "section",
                ""
            )
        ).strip()

        document = metadata.get(
            "document",
            ""
        )

        source = metadata.get(
            "source",
            ""
        )

        doc_id = (
            document,
            section,
            source
        )

        if doc_id in seen:

            continue

        seen.add(doc_id)

        text = chunk.get(
            "text",
            ""
        )

        kw_score = keyword_score(
            query,
            text,
            metadata
        )

        # Keep semantic similarity dominant.
        final_score = (
            float(distance)
            +
            kw_score * 0.02
        )

        results.append({

            "text": text,

            "metadata": metadata,

            "score": final_score,

            "dense_score": float(
                distance
            ),

            "keyword_score": kw_score,

            "best_query": query,

        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    results = results[:k]

    print(
        "\nDense results returned:",
        len(results)
    )

    print(
        "\nDense candidate sections:"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{i:02d}. Section "
            f"{result['metadata'].get('section', '?')}"
        )

    return results


# ============================================================
# MULTI-QUERY DENSE RETRIEVAL
# ============================================================

def multi_query_dense_search(
    queries,
    k=10
):

    combined = {}

    retrieval_k = min(
        max(k * 5, 50),
        index.ntotal
    )

    for query in queries:

        print("\n----------------------------------------")
        print("FAISS MULTI-QUERY")
        print("----------------------------------------")
        print(
            "Query:",
            query
        )

        query_embedding = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        distances, indices = index.search(
            query_embedding,
            retrieval_k
        )

        for rank, (
            idx,
            distance
        ) in enumerate(
            zip(
                indices[0],
                distances[0]
            ),
            start=1
        ):

            if idx < 0:

                continue

            if idx >= len(chunks):

                continue

            chunk = chunks[idx]

            metadata = chunk.get(
                "metadata",
                {}
            )

            section = str(
                metadata.get(
                    "section",
                    ""
                )
            ).strip()

            document = metadata.get(
                "document",
                ""
            )

            source = metadata.get(
                "source",
                ""
            )

            doc_id = (
                document,
                section,
                source
            )

            semantic_score = float(
                distance
            )

            if doc_id not in combined:

                combined[doc_id] = {

                    "text": chunk.get(
                        "text",
                        ""
                    ),

                    "metadata": metadata,

                    "score": semantic_score,

                    "dense_score": semantic_score,

                    "best_query": query,

                    "best_rank": rank,

                }

            else:

                existing = combined[
                    doc_id
                ]

                if semantic_score > existing[
                    "dense_score"
                ]:

                    existing[
                        "dense_score"
                    ] = semantic_score

                    existing[
                        "score"
                    ] = semantic_score

                    existing[
                        "best_query"
                    ] = query

                    existing[
                        "best_rank"
                    ] = rank

    results = list(
        combined.values()
    )

    # --------------------------------------------------------
    # KEYWORD BOOST
    # --------------------------------------------------------

    original_query = queries[0]

    for result in results:

        kw = keyword_score(
            original_query,
            result["text"],
            result["metadata"]
        )

        result[
            "keyword_score"
        ] = kw

        result["score"] = (
            result["dense_score"]
            +
            kw * 0.02
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    results = results[:k]

    print(
        f"\nMulti-query dense results: "
        f"{len(results)}"
    )

    print(
        "\nTop dense candidates:"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        section = result[
            "metadata"
        ].get(
            "section",
            "?"
        )

        print(
            f"{i:02d}. Section {section} "
            f"score={result['score']:.6f}"
        )

    return results


# ============================================================
# MAIN DENSE SEARCH ENTRY POINT
# ============================================================

def retrieve_dense(
    query,
    k=10
):

    queries = generate_retrieval_queries(
        query
    )

    print(
        "\nGenerated retrieval queries:"
    )

    for i, q in enumerate(
        queries,
        start=1
    ):

        print(
            f"{i:02d}. {q}"
        )

    return multi_query_dense_search(
        queries,
        k=k
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def search_documents_legacy(
    query,
    k=10
):

    return retrieve_dense(
        query,
        k=k
    )


# Existing imports in your project can continue using this.
search_documents = retrieve_dense