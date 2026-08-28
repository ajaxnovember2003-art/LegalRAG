import pickle
import math
import re
from collections import Counter


# ============================================================
# CONFIG
# ============================================================

CHUNKS_PATH = "data/vector_store/chunks.pkl"


# ============================================================
# LOAD CHUNKS
# ============================================================

with open(
    CHUNKS_PATH,
    "rb"
) as f:

    chunks = pickle.load(f)


# ============================================================
# TOKENIZER
# ============================================================

def tokenize(text):

    return re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )


# ============================================================
# BM25
# ============================================================

class BM25:

    def __init__(
        self,
        documents,
        k1=1.5,
        b=0.75
    ):

        self.documents = documents

        self.k1 = k1

        self.b = b

        self.tokenized_docs = [
            tokenize(doc)
            for doc in documents
        ]

        self.doc_lengths = [
            len(doc)
            for doc in self.tokenized_docs
        ]

        self.avgdl = (
            sum(self.doc_lengths)
            /
            max(len(self.doc_lengths), 1)
        )

        self.N = len(
            self.tokenized_docs
        )

        self.df = Counter()

        for doc in self.tokenized_docs:

            for term in set(doc):

                self.df[term] += 1

    def score(
        self,
        query
    ):

        query_tokens = tokenize(
            query
        )

        scores = []

        for doc_tokens, dl in zip(
            self.tokenized_docs,
            self.doc_lengths
        ):

            frequencies = Counter(
                doc_tokens
            )

            score = 0.0

            for term in query_tokens:

                if term not in frequencies:

                    continue

                df = self.df.get(
                    term,
                    0
                )

                idf = math.log(
                    1
                    +
                    (
                        self.N
                        -
                        df
                        +
                        0.5
                    )
                    /
                    (
                        df
                        +
                        0.5
                    )
                )

                tf = frequencies[
                    term
                ]

                numerator = (
                    tf *
                    (
                        self.k1
                        +
                        1
                    )
                )

                denominator = (
                    tf
                    +
                    self.k1
                    *
                    (
                        1
                        -
                        self.b
                        +
                        self.b
                        *
                        dl
                        /
                        self.avgdl
                    )
                )

                score += (
                    idf
                    *
                    numerator
                    /
                    denominator
                )

            scores.append(
                score
            )

        return scores


# ============================================================
# BUILD BM25
# ============================================================

texts = [
    chunk.get(
        "text",
        ""
    )
    for chunk in chunks
]

bm25 = BM25(
    texts
)


# ============================================================
# SEARCH
# ============================================================

def search_bm25(
    query,
    k=10
):

    scores = bm25.score(
        query
    )

    ranked = sorted(
        enumerate(scores),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for idx, score in ranked[:k]:

        chunk = chunks[idx]

        results.append({

            "text": chunk.get(
                "text",
                ""
            ),

            "metadata": chunk.get(
                "metadata",
                {}
            ),

            "score": float(
                score
            ),

        })

    print(
        "\nBM25 candidate sections:"
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
            f"{i:02d}. Section {section}"
        )

    return results