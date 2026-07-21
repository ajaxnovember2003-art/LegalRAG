import re


def clean_section(text):

    # Remove content before first legal sentence
    match = re.search(
        r'\d+\.\s*(?:\(\d+\))?',
        text
    )

    if match:
        text = text[match.start():]


    # Remove Gazette/OCR noise patterns

    patterns = [

        r'vlk.*?',

        r'Hkkx.*?',

        r'izkf/kdkj.*?',

        r'NEW DELHI.*?\(SAKA\)',

        r'bl Hkkx esa.*?',

        r'jftLVªh.*?',

        r'REGISTERED NO.*?',

        r'MINISTRY OF LAW AND JUSTICE.*?',

        r'सी.*?',

        r'CG-DL.*?'

    ]


    for pattern in patterns:
        text = re.sub(
            pattern,
            '',
            text,
            flags=re.DOTALL
        )


    # Fix spacing

    text = re.sub(
        r'\s+',
        ' ',
        text
    )


    return text.strip()


def remove_gazette_header(text):

    start = text.find(
        "1. (1) This Act may be called"
    )

    if start != -1:
        text = text[start:]


    return text