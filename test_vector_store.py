from backend.app.services.pdf_loader import extract_text_from_pdf
from backend.app.services.text_cleaner import clean_text, remove_gazette_header
from backend.app.services.section_extractor import extract_sections
from backend.app.services.metadata_builder import build_metadata
from backend.app.services.chunker import chunk_documents
from backend.app.services.embedding import generate_embeddings
from backend.app.services.vector_store import create_faiss_index, save_index


file_path = "data/raw/statutes/BNS.pdf"


text = extract_text_from_pdf(file_path)


cleaned = remove_gazette_header(
    clean_text(text)
)


sections = extract_sections(cleaned)


documents = build_metadata(
    sections,
    "Bharatiya Nyaya Sanhita"
)


chunks = chunk_documents(documents)


embeddings = generate_embeddings(chunks)


index = create_faiss_index(
    embeddings
)


save_index(
    index,
    chunks
)


print("Total vectors:", index.ntotal)   