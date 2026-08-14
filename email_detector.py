import re


EMAIL_PATTERN = r'[\w\.-]+@[\w\.-]+\.\w+'


def detect_emails(text):
    """
    Detect email addresses from a text string.

    Returns:
        list[str]: unique email addresses found in the text.
    """

    matches = re.findall(EMAIL_PATTERN, text)

    # Remove duplicates while preserving order
    unique_emails = list(dict.fromkeys(matches))

    return unique_emails
