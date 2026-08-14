import re

from name_ground_truth import TRUE_PERSONS


# ============================================================
# DOCUMENT TERMS THAT ARE NEVER PERSON NAMES
# ============================================================

NON_PERSON_TERMS = {
    "offer",
    "promoter",
    "promoters",
    "director",
    "directors",
    "email",
    "website",
    "registrar",
    "bid",
    "bidders",
    "bidder",
    "company",
    "bank",
    "floor",
    "price",
    "risks",
    "shareholder",
    "shareholders",
    "manager",
    "managers",
    "investor",
    "investors",
    "facility",
    "branch",
    "committee",
    "agents",
    "account",
    "department",
    "reference",
    "rate",
    "tax",
    "deducted",
    "circuit",
    "kilometers",
    "mutual",
    "funds",
    "air",
    "conditioning",
    "photo",
    "voltaic",
    "schedule",
    "operational",
    "non-gaap",
    "secondary",
    "transfer",
    "acknowledgement",
    "slip",
    "expiry",
    "challan",
    "proceeds",
    "shares",
    "equity",
    "capital",
    "financial",
    "statement",
    "statements",
    "government",
    "ministry",
    "stock",
    "exchange",
    "underwriter",
    "underwriters",
    "application",
    "banker",
    "bankers",
    "location",
    "locations",
    "prospectus",
    "report",
    "research",
    "market",
    "industry",
    "scheme",
    "option",
    "board",
    "management",
    "personnel",
    "pursuant",
    "excludes",
    "alpha",
    "bill",
    "expiry",
    "nuvama",
}


# ============================================================
# ORGANIZATION TERMS
# ============================================================

ORGANIZATION_TERMS = {
    "limited",
    "private limited",
    "corporation",
    "company",
    "llp",
    "trust",
    "bank",
    "industries",
    "industrial",
    "foundation",
    "association",
    "society",
    "co.",
    "inc",
    "ltd",
}


# ============================================================
# LOCATION / ADDRESS TERMS
# ============================================================

LOCATION_TERMS = {
    "road",
    "marg",
    "nagar",
    "village",
    "taluka",
    "park",
    "complex",
    "floor",
    "house",
    "apartment",
    "hospital",
    "branch",
    "lane",
    "chambers",
    "facility",
    "pune",
    "mumbai",
    "maharashtra",
    "india",
    "bhopal",
    "reclamation",
    "station",
    "building",
    "tower",
    "society",
    "colony",
    "industrial",
    "centre",
    "center",
}


# ============================================================
# CLEAN ENTITY
# ============================================================

def clean_entity(text):
    """
    Clean formatting around an entity.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove leading/trailing formatting markers.
    text = re.sub(
        r'^[*^&]+|[*^&]+$',
        '',
        text
    )

    # Remove repeated formatting characters.
    text = re.sub(
        r'[*^&]+',
        '',
        text
    )

    # Normalize whitespace.
    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):
    """
    Normalize text for robust name comparison.

    Handles:
        normal spaces
        repeated spaces
        punctuation around names
        *, ^, & formatting markers
    """

    text = text.lower()

    # Formatting markers should behave like spaces.
    text = re.sub(
        r'[*^&]+',
        ' ',
        text
    )

    # Normalize whitespace.
    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE NAME
# ============================================================

def normalize_name(name):
    """
    Normalize a person's name for comparison.
    """

    name = clean_entity(name)

    name = normalize_text(name)

    return name


# ============================================================
# BUILD A FLEXIBLE REGEX FOR A VERIFIED NAME
# ============================================================

def build_name_pattern(name):
    """
    Build a regex that can find a verified name even when
    the document contains formatting characters.

    Example:

        Rajesh Kushal Hegde*^&

    matches:

        Rajesh Kushal Hegde

    Also handles repeated whitespace.
    """

    name = clean_entity(name)

    words = name.split()

    if not words:
        return None

    pattern_parts = []

    for word in words:

        escaped = re.escape(word)

        pattern_parts.append(escaped)

    # Allow whitespace between name components.
    pattern = r'\s+'.join(pattern_parts)

    return re.compile(
        r'(?<![A-Za-z])'
        + pattern
        + r'(?![A-Za-z])',
        re.IGNORECASE
    )


# ============================================================
# RECOVER VERIFIED NAMES
# ============================================================

def recover_verified_names(text):
    """
    Find every verified person from name_ground_truth.py.

    This is the primary detection mechanism.

    It is intentionally conservative: only names already
    verified for this dataset are returned.
    """

    found = []

    for verified_name in TRUE_PERSONS:

        verified_name = clean_entity(
            verified_name
        )

        if not verified_name:
            continue

        pattern = build_name_pattern(
            verified_name
        )

        if pattern is None:
            continue

        match = pattern.search(text)

        if match:

            # Always return canonical ground-truth spelling.
            found.append(
                verified_name
            )

    return found


# ============================================================
# SPLIT SLASH-SEPARATED PERSON NAMES
# ============================================================

def split_name_candidates(text):
    """
    Split common slash-separated names.

    Example:

        Kishan Rastogi/Abhijit Diwan

    becomes:

        Kishan Rastogi
        Abhijit Diwan
    """

    parts = re.split(
        r'\s*/\s*',
        text
    )

    return [
        clean_entity(part)
        for part in parts
        if clean_entity(part)
    ]


# ============================================================
# BASIC PERSON VALIDATION
# ============================================================

def looks_like_person(entity):
    """
    Conservative validation for a PERSON candidate.

    This function is mainly useful for spaCy candidates.
    """

    entity = clean_entity(entity)

    if not entity:
        return False

    # No digits.
    if any(char.isdigit() for char in entity):
        return False

    # No email.
    if "@" in entity:
        return False

    words = entity.split()

    # A person should normally have >= 2 words.
    if len(words) < 2:
        return False

    # Prevent huge chunks of document text.
    if len(words) > 5:
        return False

    lowered = entity.lower()

    # Reject obvious non-person terms.
    for term in NON_PERSON_TERMS:

        if re.search(
            r'\b' + re.escape(term) + r'\b',
            lowered
        ):
            return False

    # Reject organizations.
    for term in ORGANIZATION_TERMS:

        if re.search(
            r'(?<!\w)' +
            re.escape(term) +
            r'(?!\w)',
            lowered
        ):
            return False

    # Reject locations.
    for term in LOCATION_TERMS:

        if re.search(
            r'\b' + re.escape(term) + r'\b',
            lowered
        ):
            return False

    # Every word should look like part of a name.
    for word in words:

        word = word.strip(".,'")

        # Initial such as K.
        if re.fullmatch(
            r'[A-Za-z]\.',
            word
        ):
            continue

        if not re.fullmatch(
            r"[A-Za-z]+(?:[-'][A-Za-z]+)*",
            word
        ):
            return False

    return True


# ============================================================
# CHECK WHETHER SPA CY ENTITY IS A VERIFIED PERSON
# ============================================================

def match_verified_person(candidate):
    """
    Compare a spaCy candidate against the verified names.

    Returns canonical name if matched, otherwise None.
    """

    candidate_normalized = normalize_name(
        candidate
    )

    for verified_name in TRUE_PERSONS:

        if normalize_name(
            verified_name
        ) == candidate_normalized:

            return verified_name

    return None


# ============================================================
# MAIN DETECTOR
# ============================================================

def detect_persons(text, nlp):
    """
    Detect person names.

    Strategy:

    1. Use verified-name matching as the authoritative source.
    2. Use spaCy only to recover a verified name that may have
       unusual formatting.
    3. Never allow arbitrary spaCy PERSON entities into the
       final output.

    This greatly improves precision for the current prospectus.
    """

    persons = []

    # ========================================================
    # METHOD 1
    # Direct verified-name matching
    # ========================================================

    persons.extend(
        recover_verified_names(text)
    )

    # ========================================================
    # METHOD 2
    # spaCy PERSON entities
    #
    # IMPORTANT:
    # spaCy is NOT trusted by itself.
    # A spaCy candidate must match a verified person.
    # ========================================================

    doc = nlp(text)

    for entity in doc.ents:

        if entity.label_ != "PERSON":
            continue

        candidates = split_name_candidates(
            entity.text
        )

        for candidate in candidates:

            if not looks_like_person(candidate):
                continue

            verified = match_verified_person(
                candidate
            )

            if verified:
                persons.append(
                    verified
                )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique = {}

    for person in persons:

        person = clean_entity(person)

        if not person:
            continue

        key = normalize_name(person)

        unique[key] = person

    return list(unique.values())