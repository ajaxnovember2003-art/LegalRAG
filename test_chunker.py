from backend.app.services.pdf_loader import extract_text_from_pdf
from backend.app.services.text_cleaner import clean_text, remove_gazette_header
from backend.app.services.section_extractor import extract_sections
from backend.app.services.metadata_builder import build_metadata
from backend.app.services.chunker import chunk_documents


file_path = "data/raw/statutes/BNS.pdf"

text = extract_text_from_pdf(file_path)

cleaned = clean_text(text)
cleaned = remove_gazette_header(cleaned)

sections = extract_sections(cleaned)

documents = build_metadata(
    sections,
    "Bharatiya Nyaya Sanhita"
)

chunks = chunk_documents(documents)

print("Documents:", len(documents))
print("Chunks:", len(chunks))

print("\nFIRST CHUNK\n")
print(chunks[0])