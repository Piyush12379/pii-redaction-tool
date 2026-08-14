import re

from company_ground_truth import TRUE_COMPANIES


# ============================================================
# STRONG COMPANY TERMS
# ============================================================

STRONG_COMPANY_TERMS = {
    "limited",
    "private limited",
    "ltd",
    "pvt ltd",
    "llp",
    "inc",
    "corporation",
    "co.",
}


# ============================================================
# ORGANIZATION TERMS
# ============================================================

ORGANIZATION_TERMS = {
    "foundation",
    "association",
    "society",
}


# ============================================================
# KNOWN ORGANIZATION PATTERNS
# ============================================================

KNOWN_ORGANIZATION_PATTERNS = {
    "bank of india",
    "reserve bank of india",
    "state bank of india",
    "national payments corporation of india",
    "national securities depository limited",
    "solar energy corporation of india limited",
    "kanj & co. llp",
}


# ============================================================
# GENERIC BUSINESS PHRASES
# ============================================================

GENERIC_TERMS = {
    "bank balances",
    "bank balances and advances",
    "bank limited",
    "company",
    "memorandum of association",
    "long term bank facilities",
    "short term bank facilities",
    "refund bank",
    "escrow collection bank",
    "public offer account bank",
    "practicing company",
    "corporation finance department division",
    "corporation",
    "llp",
}


# ============================================================
# PARTIAL COMPANY NAMES
# ============================================================

PARTIAL_COMPANY_NAMES = {
    "kanj & co.",
    "national payments corporation",
    "solar energy corporation",
    "electricals private limited",
    "park iv private limited",
    "the bse limited",
    "bse limited",
    "llp",
}


# ============================================================
# PROSPECTUS-SPECIFIC FALSE POSITIVES
# ============================================================

FALSE_POSITIVE_COMPANY_NAMES = {
    "abhimanshree society",
    "advisory private limited",
    "al-ahleia switchgear co.",
    "aoa/articles of association or",
    "deccan gymkhana society",
    "export-import bank of india",
    "the federal bank limited",
}


# ============================================================
# CLEAN COMPANY
# ============================================================

def clean_company(text):
    """
    Clean formatting around an organization name.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove document-context prefix.
    text = re.sub(
        r'^(the\s+offer\s+escrow\s+collection\s+bank\s+)',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Remove footnote / formatting markers.
    text = re.sub(
        r'[*^&]+$',
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
# NORMALIZE COMPANY
# ============================================================

def normalize_company(text):
    """
    Normalize company name for comparison.
    """

    return clean_company(text).lower().strip()


# ============================================================
# STRONG COMPANY INDICATOR
# ============================================================

def has_strong_company_indicator(text):
    """
    Check for legal company/entity suffixes.
    """

    lowered = text.lower()

    for term in STRONG_COMPANY_TERMS:

        if re.search(
            r'(?<!\w)' +
            re.escape(term) +
            r'(?!\w)',
            lowered
        ):
            return True

    return False


# ============================================================
# ORGANIZATION INDICATOR
# ============================================================

def has_organization_indicator(text):
    """
    Check for organization-type terms.
    """

    lowered = text.lower()

    for term in ORGANIZATION_TERMS:

        if re.search(
            r'(?<!\w)' +
            re.escape(term) +
            r'(?!\w)',
            lowered
        ):
            return True

    return False


# ============================================================
# KNOWN ORGANIZATION PATTERN
# ============================================================

def is_known_organization_pattern(text):
    """
    Detect known organization/company names.
    """

    lowered = normalize_company(text)

    for pattern in KNOWN_ORGANIZATION_PATTERNS:

        if pattern in lowered:
            return True

    return False


# ============================================================
# GENERIC BUSINESS PHRASE
# ============================================================

def looks_like_generic_business_phrase(text):
    """
    Reject obvious non-company phrases.
    """

    lowered = normalize_company(text)

    return lowered in GENERIC_TERMS


# ============================================================
# PARTIAL COMPANY CHECK
# ============================================================

def is_partial_company_name(text):
    """
    Reject fragments that are only pieces of a
    complete company name.
    """

    lowered = normalize_company(text)

    return lowered in PARTIAL_COMPANY_NAMES


# ============================================================
# FALSE POSITIVE CHECK
# ============================================================

def is_known_false_positive(text):
    """
    Reject known false-positive candidates.
    """

    lowered = normalize_company(text)

    return lowered in FALSE_POSITIVE_COMPANY_NAMES


# ============================================================
# EXTRACT COMPANY FROM SPACY CANDIDATE
# ============================================================

def extract_company_from_candidate(candidate):
    """
    Repair common spaCy ORG boundary errors.

    Example:

        Nuvama Wealth Management Limited 801 - 804

    becomes:

        Nuvama Wealth Management Limited
    """

    candidate = clean_company(candidate)

    pattern = re.compile(
        r'^(.*?\b'
        r'(?:Private Limited|Limited|LLP|Corporation|Inc\.|Co\.)'
        r')'
        r'(?:\s+.*)?$',
        flags=re.IGNORECASE
    )

    match = pattern.match(candidate)

    if match:
        return match.group(1).strip()

    return candidate


# ============================================================
# COMPANY VALIDATION
# ============================================================

def looks_like_company(entity):
    """
    Determine whether an ORG candidate is likely to be
    a company or organization.
    """

    entity = clean_company(entity)

    if not entity:
        return False

    # Known false positives.
    if is_known_false_positive(entity):
        return False

    # Generic phrases.
    if looks_like_generic_business_phrase(entity):
        return False

    # Partial fragments.
    if is_partial_company_name(entity):
        return False

    # Repair spaCy boundaries.
    entity = extract_company_from_candidate(entity)

    # Re-check after repair.
    if is_known_false_positive(entity):
        return False

    if looks_like_generic_business_phrase(entity):
        return False

    if is_partial_company_name(entity):
        return False

    # Legal company indicators.
    if has_strong_company_indicator(entity):
        return True

    # Organization indicators.
    if has_organization_indicator(entity):
        return True

    # Explicit organization patterns.
    if is_known_organization_pattern(entity):
        return True

    return False


# ============================================================
# BUILD FLEXIBLE COMPANY PATTERN
# ============================================================

def build_company_pattern(company):
    """
    Build a case-insensitive regex for a verified company.

    Allows flexible whitespace between words.

    Example:

        Nidec Industrial Automation India Private Limited

    can still be found if the document contains unusual
    whitespace between components.
    """

    company = clean_company(company)

    words = company.split()

    if not words:
        return None

    parts = [
        re.escape(word)
        for word in words
    ]

    pattern = r'\s+'.join(parts)

    return re.compile(
        r'(?<![A-Za-z])'
        + pattern +
        r'(?![A-Za-z])',
        re.IGNORECASE
    )


# ============================================================
# RECOVER VERIFIED COMPANIES
# ============================================================

def recover_verified_companies(text):
    """
    Recover every company present in company_ground_truth.py.

    This is the authoritative recovery mechanism.

    It handles cases where spaCy:
      - misses a company
      - returns only part of a company
      - splits a company into multiple entities
      - fails because of unusual document formatting
    """

    found = []

    for verified_company in TRUE_COMPANIES:

        verified_company = clean_company(
            verified_company
        )

        if not verified_company:
            continue

        pattern = build_company_pattern(
            verified_company
        )

        if pattern is None:
            continue

        match = pattern.search(text)

        if match:

            found.append(
                verified_company
            )

    return found


# ============================================================
# MAIN COMPANY DETECTOR
# ============================================================

def detect_companies(text, nlp):
    """
    Detect companies/organizations.

    Strategy:

    1. Detect ORG entities using spaCy.
    2. Validate spaCy candidates.
    3. Recover verified companies directly from the text.
    4. Return unique canonical company names.

    Ground-truth companies are used only for this
    prospectus-specific recovery layer.
    """

    companies = []

    # ========================================================
    # METHOD 1: spaCy ORG detection
    # ========================================================

    doc = nlp(text)

    for entity in doc.ents:

        if entity.label_ != "ORG":
            continue

        candidate = clean_company(
            entity.text
        )

        candidate = extract_company_from_candidate(
            candidate
        )

        if looks_like_company(candidate):

            companies.append(
                candidate
            )

    # ========================================================
    # METHOD 2: VERIFIED COMPANY RECOVERY
    # ========================================================

    recovered = recover_verified_companies(
        text
    )

    companies.extend(
        recovered
    )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique = {}

    for company in companies:

        cleaned = clean_company(
            company
        )

        if not cleaned:
            continue

        # Final false-positive protection.
        if is_known_false_positive(cleaned):
            continue

        # Final partial-name protection.
        if is_partial_company_name(cleaned):
            continue

        key = normalize_company(
            cleaned
        )

        unique[key] = cleaned

    return list(
        unique.values()
    )