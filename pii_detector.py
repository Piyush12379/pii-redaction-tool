import spacy

from name_detector import detect_persons
from company_detector import detect_companies
from email_detector import detect_emails
from phone_detector import detect_phone_numbers
from credit_card_detector import detect_credit_cards
from ssn_detector import detect_ssns
from dob_detector import detect_dobs
from ip_detector import detect_ip_addresses


# ============================================================
# LOAD NLP MODEL
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# MAIN PII DETECTOR
# ============================================================

def detect_all_pii(text):
    """
    Detect all supported PII/entity types from a block of text.

    Returns:
        dict containing detected PII grouped by category.
    """

    results = {
        "persons": [],
        "companies": [],
        "emails": [],
        "phones": [],
        "credit_cards": [],
        "ssns": [],
        "dobs": [],
        "ip_addresses": [],
    }

    # --------------------------------------------------------
    # PERSON NAMES
    # --------------------------------------------------------

    results["persons"] = detect_persons(
        text,
        nlp
    )

    # --------------------------------------------------------
    # COMPANIES / ORGANIZATIONS
    # --------------------------------------------------------

    results["companies"] = detect_companies(
        text,
        nlp
    )

    # --------------------------------------------------------
    # EMAIL ADDRESSES
    # --------------------------------------------------------

    results["emails"] = detect_emails(
        text
    )

    # --------------------------------------------------------
    # PHONE NUMBERS
    # --------------------------------------------------------

    results["phones"] = detect_phone_numbers(
        text
    )

    # --------------------------------------------------------
    # CREDIT CARDS
    # --------------------------------------------------------

    results["credit_cards"] = detect_credit_cards(
        text
    )

    # --------------------------------------------------------
    # SSNs
    # --------------------------------------------------------

    results["ssns"] = detect_ssns(
        text
    )

    # --------------------------------------------------------
    # DATES OF BIRTH
    # --------------------------------------------------------

    results["dobs"] = detect_dobs(
        text
    )

    # --------------------------------------------------------
    # IP ADDRESSES
    # --------------------------------------------------------

    results["ip_addresses"] = detect_ip_addresses(
        text
    )

    return results


# ============================================================
# DETECT PII FROM COMPLETE DOCUMENT
# ============================================================

def detect_document_pii(blocks):
    """
    Detect PII from a list of extracted document blocks.

    Args:
        blocks: list[str]

    Returns:
        dict containing unique PII from the entire document.
    """

    results = {
        "persons": [],
        "companies": [],
        "emails": [],
        "phones": [],
        "credit_cards": [],
        "ssns": [],
        "dobs": [],
        "ip_addresses": [],
    }

    for block in blocks:

        block_results = detect_all_pii(
            block
        )

        for category in results:

            for value in block_results[category]:

                if value not in results[category]:

                    results[category].append(
                        value
                    )

    return results


# ============================================================
# COUNT TOTAL DETECTED PII
# ============================================================

def count_pii(results):
    """
    Return the total number of unique PII items detected.
    """

    total = 0

    for values in results.values():

        total += len(values)

    return total