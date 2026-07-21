from backend.app.services.section_cleaner import clean_section

def build_metadata(sections, document_name):

    documents = []

    for section in sections:

        documents.append({

            "document": document_name,

            "year": 2023,

            "section": section["section_number"],

            "text": clean_section(section["content"]),

            "source": f"{document_name}.pdf"

        })

    return documents