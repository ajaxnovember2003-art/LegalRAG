import pickle

CHUNKS_PATH = "data/vector_store/chunks.pkl"

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)

print("=" * 70)
print("SECTION 126 DATASET CHECK")
print("=" * 70)

matches = []

for i, chunk in enumerate(chunks):

    metadata = chunk.get("metadata", {})

    section = str(
        metadata.get("section", "")
    ).strip()

    if section == "126":
        matches.append((i, chunk))

print("Total chunks:", len(chunks))
print("Section 126 occurrences:", len(matches))

for i, chunk in matches:

    print("\n" + "-" * 70)
    print("CHUNK INDEX:", i)
    print("SECTION:", chunk["metadata"].get("section"))
    print("DOCUMENT:", chunk["metadata"].get("document"))
    print("SOURCE:", chunk["metadata"].get("source"))

    print("\nTEXT:")
    print(chunk["text"][:3000])

print("\n" + "=" * 70)

if not matches:
    print("❌ SECTION 126 DOES NOT EXIST IN chunks.pkl")
else:
    print("✅ SECTION 126 EXISTS IN chunks.pkl")