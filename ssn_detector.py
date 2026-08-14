import re


SSN_PATTERN = re.compile(
    r'\b\d{3}-\d{2}-\d{4}\b'
)


def detect_ssns(text):
    """
    Detect standard US Social Security Number formats.

    Returns:
        list[str]: unique SSN candidates.
    """

    matches = SSN_PATTERN.findall(text)

    return list(dict.fromkeys(matches))
