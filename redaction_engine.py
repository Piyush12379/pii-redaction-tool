import re


# ============================================================
# REDACTION LABELS
# ============================================================

REDACTION_LABELS = {
    "persons": "[REDACTED_PERSON]",
    "companies": "[REDACTED_COMPANY]",
    "emails": "[REDACTED_EMAIL]",
    "phones": "[REDACTED_PHONE]",
    "credit_cards": "[REDACTED_CREDIT_CARD]",
    "ssns": "[REDACTED_SSN]",
    "dobs": "[REDACTED_DOB]",
    "ip_addresses": "[REDACTED_IP]",
}


# ============================================================
# NORMALIZE VALUE FOR MATCHING
# ============================================================

def normalize_for_matching(value):
    """
    Normalize a detected value for case-insensitive matching.

    Whitespace is normalized but the original detected value
    is preserved when building the regex.
    """

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# ============================================================
# BUILD SAFE REGEX
# ============================================================

def build_redaction_pattern(value):
    """
    Build a regex that matches the detected value safely.

    Matching is case-insensitive.
    Whitespace inside the value can vary.
    """

    value = normalize_for_matching(value)

    if not value:
        return None

    parts = re.split(
        r"\s+",
        value
    )

    escaped_parts = [
        re.escape(part)
        for part in parts
    ]

    pattern = r"\s+".join(
        escaped_parts
    )

    return re.compile(
        pattern,
        re.IGNORECASE
    )


# ============================================================
# REDACT ONE VALUE
# ============================================================

def redact_value(text, value, replacement):
    """
    Replace every occurrence of one detected PII value.
    """

    pattern = build_redaction_pattern(
        value
    )

    if pattern is None:
        return text

    return pattern.sub(
        replacement,
        text
    )


# ============================================================
# REDACT ONE TEXT BLOCK
# ============================================================

def redact_text(text, pii_results):
    """
    Redact all detected PII from one text block.

    Args:
        text: original text
        pii_results: dictionary returned by detect_all_pii()

    Returns:
        Redacted text.
    """

    redacted_text = text

    # --------------------------------------------------------
    # Longer values first.
    #
    # This is important for names such as:
    #
    # Rajesh Hegde
    # Rajesh Kushal Hegde
    #
    # The longer name should be redacted first.
    # --------------------------------------------------------

    for category, values in pii_results.items():

        replacement = REDACTION_LABELS.get(
            category
        )

        if replacement is None:
            continue

        sorted_values = sorted(
            values,
            key=len,
            reverse=True
        )

        for value in sorted_values:

            redacted_text = redact_value(
                redacted_text,
                value,
                replacement
            )

    return redacted_text


# ============================================================
# REDACT COMPLETE DOCUMENT
# ============================================================

def redact_document_blocks(blocks, detector):
    """
    Detect and redact PII from every document block.

    Args:
        blocks:
            List of text blocks extracted from the document.

        detector:
            Function such as detect_all_pii.

    Returns:
        List of redacted blocks.
    """

    redacted_blocks = []

    for block in blocks:

        pii_results = detector(
            block
        )

        redacted = redact_text(
            block,
            pii_results
        )

        redacted_blocks.append(
            redacted
        )

    return redacted_blocks


# ============================================================
# REDACT USING ALREADY DETECTED DOCUMENT PII
# ============================================================

def redact_with_document_results(
    blocks,
    document_results
):
    """
    Redact document blocks using PII already detected
    for the complete document.

    This is useful when we want the same detection result
    to be applied consistently across the document.
    """

    redacted_blocks = []

    for block in blocks:

        redacted = redact_text(
            block,
            document_results
        )

        redacted_blocks.append(
            redacted
        )

    return redacted_blocks
