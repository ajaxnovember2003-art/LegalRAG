from typing import List


def chunk_documents(documents: List[dict], chunk_size: int = 500, overlap: int = 100):
    """
    Split legal documents into overlapping chunks.
    """

    chunks = []

    for doc in documents:

        text = doc["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunk = {
                "text": chunk_text,
                "metadata": {
                    "document": doc["document"],
                    "section": doc["section"],
                    "year": doc["year"],
                    "source": doc["source"]
                }
            }

            chunks.append(chunk)

            start += chunk_size - overlap

    return chunks