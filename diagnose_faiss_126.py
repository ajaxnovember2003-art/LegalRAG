import pickle
import faiss
import numpy as np

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

CHUNKS_PATH = "data/vector_store/chunks.pkl"
INDEX_PATH = "data/vector_store/legal.index"

# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)

index = faiss.read_index(INDEX_PATH)

print("=" * 70)
print("FAISS FULL-RANK DIAGNOSTIC — SECTION 126")
print("=" * 70)

# ------------------------------------------------------------
# IMPORTANT:
# We need the SAME embedding model used by test.py
# ------------------------------------------------------------

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("\nLoading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# ------------------------------------------------------------
# Queries to test
# ------------------------------------------------------------

queries = [
    "What is the punishment for wrongful restraint?",
    "wrongful restraint",
    "punishment for wrongful restraint",
    "Whoever wrongfully restrains any person",
    "Section 126 wrongful restraint",
]

# ------------------------------------------------------------
# Search complete FAISS index
# ------------------------------------------------------------

for query in queries:

    print("\n" + "=" * 70)
    print("QUERY:")
    print(query)
    print("=" * 70)

    embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    embedding = np.asarray(
        embedding,
        dtype="float32"
    )

    scores, indices = index.search(
        embedding,
        index.ntotal
    )

    # Find Section 126
    section_126_rank = None
    section_126_score = None

    for rank, idx in enumerate(indices[0], start=1):

        if idx < 0:
            continue

        section = str(
            chunks[idx]
            .get("metadata", {})
            .get("section", "")
        )

        if section == "126":

            section_126_rank = rank
            section_126_score = scores[0][rank - 1]

            break

    print("\nSECTION 126 RESULT:")

    if section_126_rank is not None:

        print(
            f"Rank: {section_126_rank} / {index.ntotal}"
        )

        print(
            f"FAISS score: {section_126_score:.6f}"
        )

    else:

        print("❌ Section 126 not found")

    # --------------------------------------------------------
    # Show top 10
    # --------------------------------------------------------

    print("\nTOP 10 RESULTS:")

    for rank in range(min(10, index.ntotal)):

        idx = indices[0][rank]

        section = chunks[idx].get(
            "metadata", {}
        ).get("section", "?")

        score = scores[0][rank]

        print(
            f"{rank + 1:02d}. "
            f"Section {section} "
            f"score={score:.6f}"
        )


print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)