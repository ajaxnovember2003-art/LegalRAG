import pickle
import faiss

CHUNKS_PATH = "data/vector_store/chunks.pkl"
INDEX_PATH = "data/vector_store/legal.index"

print("=" * 70)
print("INDEX / CHUNKS ALIGNMENT DIAGNOSTIC")
print("=" * 70)

# ------------------------------------------------------------
# Load chunks
# ------------------------------------------------------------

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)

print("\nTotal chunks:", len(chunks))

# ------------------------------------------------------------
# Find section 126
# ------------------------------------------------------------

section_126 = []

for i, chunk in enumerate(chunks):

    metadata = chunk.get("metadata", {})

    section = str(
        metadata.get("section", "")
    ).strip()

    if section == "126":
        section_126.append((i, chunk))


print("Section 126 occurrences:", len(section_126))

for idx, chunk in section_126:

    print("\n" + "-" * 70)

    print("PYTHON CHUNK INDEX:", idx)

    print("METADATA:")
    print(chunk.get("metadata"))

    print("\nTEXT:")
    print(chunk.get("text"))


# ------------------------------------------------------------
# Load FAISS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FAISS CHECK")
print("=" * 70)

index = faiss.read_index(INDEX_PATH)

print("FAISS vectors:", index.ntotal)
print("Chunks:", len(chunks))

if index.ntotal == len(chunks):
    print("✅ FAISS and chunks have the same size")
else:
    print("❌ FAISS and chunks SIZE MISMATCH")


# ------------------------------------------------------------
# Check exact mapping
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FAISS INDEX MAPPING")
print("=" * 70)

for idx, chunk in section_126:

    if idx < index.ntotal:

        print(
            f"Section 126 is mapped to FAISS vector {idx}"
        )

        print("Vector exists:", True)

    else:

        print(
            f"❌ Section 126 chunk index {idx} "
            f"is outside FAISS index"
        )


# ------------------------------------------------------------
# Check neighboring chunks
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("NEIGHBORING CHUNKS")
print("=" * 70)

for idx, chunk in section_126:

    start = max(0, idx - 3)
    end = min(len(chunks), idx + 4)

    for i in range(start, end):

        metadata = chunks[i].get("metadata", {})

        print(
            f"{i:03d} -> Section "
            f"{metadata.get('section')}"
        )


print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)