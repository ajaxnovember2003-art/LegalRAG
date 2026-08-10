import faiss
import pickle
import os
import numpy as np


def create_faiss_index(embeddings):

    print("Creating FAISS index...")

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    print("Embedding shape:", embeddings.shape)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print("Vectors added:", index.ntotal)

    return index



def save_index(index, chunks):

    os.makedirs(
        "data/vector_store",
        exist_ok=True
    )

    faiss.write_index(
        index,
        "data/vector_store/legal.index"
    )


    with open(
        "data/vector_store/chunks.pkl",
        "wb"
    ) as f:

        pickle.dump(
            chunks,
            f
        )


    print("Vector store saved!")



def load_index():

    index = faiss.read_index(
        "data/vector_store/legal.index"
    )


    with open(
        "data/vector_store/chunks.pkl",
        "rb"
    ) as f:

        chunks = pickle.load(f)


    return index, chunks