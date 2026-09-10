import pickle

CHUNKS_PATH = "data/vector_store/chunks.pkl"

with open(CHUNKS_PATH, "rb") as f:
    chunks = pickle.load(f)

print(f"Total chunks: {len(chunks)}")

target_sections = {
    "64",
    "103",
    "105",
    "109",
    "318",
    "351",
}

found = {}

for section in target_sections:
    found[section] = []

for i, chunk in enumerate(chunks):

    metadata = chunk.get("metadata", {})

    section = str(
        metadata.get("section", "")
    ).strip()

    if section in target_sections:

        found[section].append({
            "index": i,
            "document": metadata.get(
                "document",
                ""
            ),
            "source": metadata.get(
                "source",
                ""
            ),
            "text": chunk.get(
                "text",
                ""
            )[:500]
        })


for section in sorted(target_sections):

    matches = found[section]

    print("\n" + "=" * 70)
    print(f"SECTION {section}")
    print("=" * 70)

    if not matches:
        print("NOT FOUND IN CHUNKS")
        continue

    print(
        f"Found {len(matches)} chunk(s)"
    )

    for item in matches[:5]:

        print(
            f"\nIndex: {item['index']}"
        )

        print(
            f"Document: {item['document']}"
        )

        print(
            f"Source: {item['source']}"
        )

        print(
            f"Text: {item['text']}"
        )