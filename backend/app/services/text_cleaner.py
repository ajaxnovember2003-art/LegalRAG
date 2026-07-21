import re


def clean_text(text):

    # Remove extra spaces and new lines
    text = re.sub(r'\s+', ' ', text)


    # Remove page number patterns
    text = re.sub(
        r'\b\d+\s*\|\s*\d+\b',
        '',
        text
    )


    # Remove Gazette headers
    remove_patterns = [

        r'PUBLISHED BY AUTHORITY',

        r'MINISTRY OF LAW AND JUSTICE',

        r'\(Legislative Department\)',

        r'NEW DELHI.*?\(SAKA\)',

        r'REGISTERED NO\..*?',

        r'CG-DL.*?',

    ]


    for pattern in remove_patterns:
        text = re.sub(
            pattern,
            '',
            text,
            flags=re.DOTALL
        )


    # Remove Gazette language artifacts
    garbage_patterns = [

    r'EXTRAORDINARY',

    r'lañ\s*\d+',

    r'No\.\s*\d+',

    r'bl Hkkx esa fHkUu.*?A',

    r'Separate paging is given.*?compilation\.',
    
    ]


    for pattern in garbage_patterns:
        text = re.sub(
            pattern,
            '',
            text,
            flags=re.DOTALL
        )


    return text.strip()



def remove_gazette_header(text):

    start = text.find(
        "1. (1) This Act may be called"
    )


    if start != -1:
        text = text[start:]


    return text