import re


def extract_sections(text):

    sections = []

    # Detect all section numbers
    pattern = r'(?<!\d)(\d{1,3})\.\s'

    matches = list(re.finditer(pattern, text))


    for i, match in enumerate(matches):

        section_number = match.group(1)

        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)


        content = text[start:end]


        # Ignore very small false matches
        if len(content) > 50:

            sections.append({
                "section_number": section_number,
                "content": content.strip()
            })


    return sections