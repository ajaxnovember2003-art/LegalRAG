from typing import List


def chunk_documents(documents: List[dict]):

    """
    Legal document chunking.
    Keeps each section as a separate chunk.
    """

    chunks = []

    for doc in documents:

        chunk = {
            "text": doc["text"],

            "metadata": {
                "document": doc["document"],
                "section": doc["section"],
                "year": doc["year"],
                "source": doc["source"]
            }
        }

        chunks.append(chunk)

    return chunks