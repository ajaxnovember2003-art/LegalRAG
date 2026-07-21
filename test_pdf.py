from backend.app.services.pdf_loader import extract_text_from_pdf
from backend.app.services.text_cleaner import clean_text, remove_gazette_header
from backend.app.services.section_extractor import extract_sections
from backend.app.services.metadata_builder import build_metadata


file_path = "data/raw/statutes/BNS.pdf"


text = extract_text_from_pdf(file_path)


cleaned_text = clean_text(text)


cleaned_text = remove_gazette_header(cleaned_text)


sections = extract_sections(cleaned_text)


documents = build_metadata(
    sections,
    "Bharatiya Nyaya Sanhita"
)


print("Total Sections Found:", len(sections))


for i, section in enumerate(sections[:5]):

    print("\n====================")
    print("CLEAN SECTION", i+1)
    print("====================")

    print(section["content"][:500])