import os
import json

print("=" * 70)
print("SECTION 126 CORPUS DIAGNOSTIC")
print("=" * 70)

# Search all JSON/JSONL/TXT files in the project
extensions = {".json", ".jsonl", ".txt", ".csv"}

found = []

for root, dirs, files in os.walk("."):
    # Ignore virtual environment and cache directories
    dirs[:] = [
        d for d in dirs
        if d not in {".venv", "__pycache__", ".git"}
    ]

    for filename in files:
        if os.path.splitext(filename)[1].lower() not in extensions:
            continue

        path = os.path.join(root, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            # Look for several possible representations
            patterns = [
                "Section 126",
                "section 126",
                '"126"',
                "'126'",
                "wrongful restraint",
                "wrongful restraint"
            ]

            matches = [p for p in patterns if p in text]

            if matches:
                found.append((path, matches, text))

        except Exception as e:
            print(f"Could not read {path}: {e}")


print(f"\nFiles containing possible matches: {len(found)}")

for path, matches, text in found:
    print("\n" + "-" * 70)
    print("FILE:", path)
    print("MATCHES:", matches)

    # Print relevant context
    lower = text.lower()

    positions = []

    for term in [
        "section 126",
        "wrongful restraint"
    ]:
        start = 0

        while True:
            pos = lower.find(term, start)

            if pos == -1:
                break

            positions.append(pos)
            start = pos + len(term)

    for pos in positions[:10]:
        start = max(0, pos - 500)
        end = min(len(text), pos + 1000)

        print("\nCONTEXT:")
        print(text[start:end])


print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)