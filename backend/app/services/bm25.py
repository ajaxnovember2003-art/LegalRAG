import pickle
import re
from rank_bm25 import BM25Okapi


CHUNKS_PATH = "data/vector_store/chunks.pkl"


print("Loading chunks for BM25...")

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)


def tokenize(text):
    """
    Convert text into tokens for BM25.
    """
    return re.findall(r"\b\w+\b", text.lower())


print("Building BM25 index...")

corpus = [
    tokenize(chunk["text"])
    for chunk in chunks
]

bm25 = BM25Okapi(corpus)

print("BM25 Loaded!")
print("Total documents:", len(corpus))


def search_bm25(query, k=20):

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    ranked_indices = scores.argsort()[::-1][:k]

    results = []

    for idx in ranked_indices:

        results.append(
            {
                "index": int(idx),
                "score": float(scores[idx])
            }
        )

    return results