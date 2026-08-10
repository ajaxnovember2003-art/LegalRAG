import faiss

path = "data/vector_store/legal.index"

index = faiss.read_index(path)

print("Loaded successfully")
print("Vectors:", index.ntotal)
print("Dimension:", index.d)