import re


# ============================================================
# Indian phone number patterns
# ============================================================

PHONE_PATTERNS = [

    # --------------------------------------------------------
    # +91 mobile
    #
    # Examples:
    # +91 81081 14949
    # +91 8879770456
    # + 91 91586 40360
    # --------------------------------------------------------

    re.compile(
        r'(?<!\d)'
        r'\+\s*91'
        r'(?:[\s.-]*)'
        r'(?:[6-9]\d{4}[\s.-]?\d{5}|[6-9]\d{9})'
        r'(?!\d)',
        re.IGNORECASE
    ),


    # --------------------------------------------------------
    # +91 Indian landline
    #
    # Examples:
    # +91 20 4505 3237
    # +91 22 40094400
    # +91 (20) 6729 5100
    # +91-20-26234000
    # --------------------------------------------------------

    re.compile(
        r'(?<!\d)'
        r'\+\s*91'
        r'(?:[\s.-]*)'
        r'\(?'
        r'(?:11|20|22|40|44|79)'
        r'\)?'
        r'(?:[\s.-]*)'
        r'\d{4}'
        r'(?:[\s.-]?)'
        r'\d{4}'
        r'(?!\d)',
        re.IGNORECASE
    ),


    # --------------------------------------------------------
    # Indian landline without country code
    #
    # Example:
    # 022-68052182
    # --------------------------------------------------------

    re.compile(
        r'(?<!\d)'
        r'0(?:11|20|22|40|44|79)'
        r'[\s.-]*'
        r'\d{4}'
        r'[\s.-]?'
        r'\d{4}'
        r'(?!\d)'
    ),
]


def normalize_phone(phone):
    """
    Normalize a phone number for comparison.

    Keeps digits only.

    Example:
        +91 22 4009 4400
        ->
        912240094400
    """

    return re.sub(r'\D', '', phone)


def count_digits(value):
    """
    Count digits in a phone candidate.
    """

    return sum(char.isdigit() for char in value)


def looks_like_year(value):
    """
    Reject standalone years such as:

        2022
        2025
        1979
    """

    value = value.strip()

    return bool(
        re.fullmatch(
            r'(?:19|20)\d{2}',
            value
        )
    )


def looks_like_year_range(value):
    """
    Reject values such as:

        2022-2023
        2024–2025
    """

    value = value.strip()

    return bool(
        re.fullmatch(
            r'(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}',
            value
        )
    )


def looks_like_phone(value):
    """
    Validate a phone candidate.

    The candidate must already have been matched by one
    of the strict Indian phone-number patterns.
    """

    value = value.strip()

    digit_count = count_digits(value)

    # Indian numbers in this detector must contain
    # either:
    #   +91 + 10 digits
    # or:
    #   0 + STD code + subscriber number
    if digit_count < 10:
        return False

    # Reject years.
    if looks_like_year(value):
        return False

    # Reject year ranges.
    if looks_like_year_range(value):
        return False

    return True


def detect_phone_numbers(text):
    """
    Detect Indian phone numbers from text.

    Supports:

        +91 20 4505 3237
        +91 20 45053237
        +91 22 40094400
        +91 22 6807 7100
        +91 (20) 6729 5100
        +91-20-26234000
        +91 81081 14949
        +91 8879770456
        022-68052182

    Does NOT treat arbitrary 10+ digit numbers as phone numbers.
    """

    phones = []

    for pattern in PHONE_PATTERNS:

        matches = pattern.findall(text)

        for candidate in matches:

            candidate = candidate.strip()

            if looks_like_phone(candidate):
                phones.append(candidate)

    # --------------------------------------------------------
    # Remove duplicates while preserving original formatting.
    # --------------------------------------------------------

    unique = []

    seen = set()

    for phone in phones:

        normalized = normalize_phone(phone)

        if normalized not in seen:

            seen.add(normalized)
            unique.append(phone)

    return unique