import re


DATE_PATTERN = (
    r'(?:'
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    r'|'
    r'\d{1,2}\s+'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{4}'
    r'|'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2},\s+\d{4}'
    r')'
)


DOB_PATTERN = re.compile(
    r'\b(?:'
    r'date\s+of\s+birth'
    r'|dob'
    r'|d\.o\.b'
    r'|birth\s+date'
    r'|born'
    r')'
    r'\s*[:\-]?\s*'
    r'(' + DATE_PATTERN + r')',
    re.IGNORECASE
)


def detect_dobs(text):
    """
    Detect dates explicitly associated with DOB-related labels.
    """

    matches = DOB_PATTERN.findall(text)

    return list(dict.fromkeys(matches))