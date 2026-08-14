import re


INDIAN_STATES = {
    "maharashtra",
    "madhya pradesh",
    "karnataka",
    "gujarat",
    "delhi",
    "tamil nadu",
    "telangana",
    "andhra pradesh",
    "kerala",
    "rajasthan",
    "west bengal",
    "uttar pradesh",
    "bihar",
    "punjab",
    "haryana",
    "odisha",
}


ADDRESS_KEYWORDS = [
    "road",
    "street",
    "lane",
    "marg",
    "nagar",
    "colony",
    "society",
    "building",
    "tower",
    "house",
    "apartment",
    "flat",
    "village",
    "taluka",
    "district",
    "plot",
    "floor",
    "complex",
    "park",
    "industrial area",
    "business centre",
    "opp",
    "opposite",
]


PIN_PATTERN = re.compile(
    r"\b[1-9][0-9]{2}\s?[0-9]{3}\b"
)


def normalize_address(text):
    """
    Normalize whitespace and formatting.
    """

    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_pin(text):
    """
    Check for an Indian PIN code.
    """

    return bool(PIN_PATTERN.search(text))


def contains_address_keyword(text):
    """
    Check for common address terminology.
    """

    lowered = text.lower()

    return any(
        keyword in lowered
        for keyword in ADDRESS_KEYWORDS
    )


def contains_indian_state(text):
    """
    Check whether an Indian state is mentioned.
    """

    lowered = text.lower()

    return any(
        state in lowered
        for state in INDIAN_STATES
    )


def has_address_number(text):
    """
    Check whether the text contains a plausible
    house/plot/building number.
    """

    return bool(
        re.search(
            r"\b(?:\d+[A-Za-z]?|\d+/\d+|\d+-\d+)\b",
            text
        )
    )


def looks_like_address(text):
    """
    Determine whether a text segment is likely to be
    a physical/mailing address.
    """

    text = normalize_address(text)

    if not text:
        return False

    lower = text.lower()

    # --------------------------------------------------
    # Reject obvious prose / explanatory sentences.
    # --------------------------------------------------

    prose_markers = [
        "unless the context",
        "we are",
        "we cannot",
        "we have",
        "we had",
        "our manufacturing",
        "our company",
        "the company is",
        "the company has",
        "the offer is",
        "for further details",
        "for further information",
        "in accordance with",
        "pursuant to",
        "we propose",
        "we purchase",
        "we procure",
        "while we",
        "there can be no assurance",
        "the prospectus",
        "the price band",
        "the registered office of our company located",
        "the corporate office of our company located",
    ]

    if any(marker in lower for marker in prose_markers):
        return False

    # --------------------------------------------------
    # Reject obvious contact-information blocks.
    # --------------------------------------------------

    contact_markers = [
        "telephone:",
        "telephone ",
        "email:",
        "e-mail:",
        "website:",
        "contact person:",
        "investor grievance",
        "sebi registration number",
        "firm registration number",
        "peer review number",
    ]

    if any(marker in lower for marker in contact_markers):
        return False

    # --------------------------------------------------
    # Reject address labels / explanatory address blocks.
    # --------------------------------------------------

    if lower.startswith("corporate office:"):
        return False

    if lower.startswith("registered office:"):
        return False

    if lower.startswith(
        "ksh international limited, a public limited company"
    ):
        return False

    # --------------------------------------------------
    # Reject small location-only fragments.
    # Example:
    # "Taluka Khed, District Pune – 410 501"
    # --------------------------------------------------

    if re.fullmatch(
        r"taluka\s+[\w\s-]+,\s*district\s+[\w\s-]+"
        r"\s*[–-]\s*[1-9][0-9]{2}\s?[0-9]{3}",
        lower
    ):
        return False

    # --------------------------------------------------
    # Strong signal:
    # Indian PIN + address terminology.
    # --------------------------------------------------

    if contains_pin(text) and contains_address_keyword(text):
        return True

    return False


def split_into_segments(text):
    """
    Split a document block into smaller segments.
    """

    # First split on newlines.
    lines = re.split(r"\n+", text)

    segments = []

    for line in lines:

        line = normalize_address(line)

        if not line:
            continue

        # Also split very long sentences.
        parts = re.split(
            r"(?<=[.;])\s+",
            line
        )

        for part in parts:

            part = normalize_address(part)

            if part:
                segments.append(part)

    return segments


def detect_addresses(text):
    """
    Detect address-like segments from a text block.
    """

    segments = split_into_segments(text)

    addresses = []

    for segment in segments:

        if looks_like_address(segment):
            addresses.append(segment)

    return list(dict.fromkeys(addresses))