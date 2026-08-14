import spacy

from extract_text import extract_document_text

from name_detector import detect_persons
from company_detector import detect_companies
from email_detector import detect_emails
from phone_detector import detect_phone_numbers
from credit_card_detector import detect_credit_cards
from ssn_detector import detect_ssns
from dob_detector import detect_dobs
from ip_detector import detect_ip_addresses


INPUT_FILE = "Prospectus.docx"
REDACTED_FILE = "Redacted_Prospectus.docx"


# ============================================================
# REDACTION MARKERS
# ============================================================

REDACTION_MARKERS = {
    "PERSON": "[REDACTED_PERSON]",
    "COMPANY": "[REDACTED_COMPANY]",
    "EMAIL": "[REDACTED_EMAIL]",
    "PHONE": "[REDACTED_PHONE]",
    "CREDIT_CARD": "[REDACTED_CREDIT_CARD]",
    "SSN": "[REDACTED_SSN]",
    "DOB": "[REDACTED_DOB]",
    "IP_ADDRESS": "[REDACTED_IP_ADDRESS]",
}


# ============================================================
# LOAD DOCUMENTS
# ============================================================

print("=" * 80)
print("PHASE 12 - FINAL REDACTION VALIDATION")
print("=" * 80)

original_blocks = extract_document_text(INPUT_FILE)
redacted_blocks = extract_document_text(REDACTED_FILE)

original_text = "\n".join(original_blocks)
redacted_text = "\n".join(redacted_blocks)


print()
print("DOCUMENT INFORMATION")
print("-" * 80)

print("Original blocks :", len(original_blocks))
print("Redacted blocks :", len(redacted_blocks))
print("Original chars  :", len(original_text))
print("Redacted chars  :", len(redacted_text))


# ============================================================
# COUNT REDACTION MARKERS
# ============================================================

print()
print("REDACTION MARKERS")
print("-" * 80)

marker_counts = {}
total_markers = 0

for pii_type, marker in REDACTION_MARKERS.items():

    count = redacted_text.count(marker)

    marker_counts[pii_type] = count
    total_markers += count

    print(f"{pii_type:<15}: {count}")


print()
print("TOTAL REDACTION MARKERS:", total_markers)


# ============================================================
# LOAD SPACY
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# DETECT REMAINING PII
# ============================================================

def detect_remaining_pii():

    remaining = {
        "PERSON": set(),
        "COMPANY": set(),
        "EMAIL": set(),
        "PHONE": set(),
        "CREDIT_CARD": set(),
        "SSN": set(),
        "DOB": set(),
        "IP_ADDRESS": set(),
    }

    for block in redacted_blocks:

        # ----------------------------------------------------
        # PERSONS
        # ----------------------------------------------------

        persons = detect_persons(block, nlp)

        for person in persons:
            remaining["PERSON"].add(person)

        # ----------------------------------------------------
        # COMPANIES
        # ----------------------------------------------------

        companies = detect_companies(block, nlp)

        for company in companies:
            remaining["COMPANY"].add(company)

        # ----------------------------------------------------
        # EMAILS
        # ----------------------------------------------------

        emails = detect_emails(block)

        for email in emails:
            remaining["EMAIL"].add(email)

        # ----------------------------------------------------
        # PHONES
        # ----------------------------------------------------

        phones = detect_phone_numbers(block)

        for phone in phones:
            remaining["PHONE"].add(phone)

        # ----------------------------------------------------
        # CREDIT CARDS
        # ----------------------------------------------------

        cards = detect_credit_cards(block)

        for card in cards:
            remaining["CREDIT_CARD"].add(card)

        # ----------------------------------------------------
        # SSNs
        # ----------------------------------------------------

        ssns = detect_ssns(block)

        for ssn in ssns:
            remaining["SSN"].add(ssn)

        # ----------------------------------------------------
        # DOBs
        # ----------------------------------------------------

        dobs = detect_dobs(block)

        for dob in dobs:
            remaining["DOB"].add(dob)

        # ----------------------------------------------------
        # IP ADDRESSES
        # ----------------------------------------------------

        ips = detect_ip_addresses(block)

        for ip in ips:
            remaining["IP_ADDRESS"].add(ip)

    return remaining


# ============================================================
# RUN LEAK CHECK
# ============================================================

print()
print("ORIGINAL PII LEAK CHECK")
print("-" * 80)

remaining = detect_remaining_pii()

remaining_total = 0

for pii_type, values in remaining.items():

    count = len(values)
    remaining_total += count

    print(f"{pii_type:<15}: {count}")

    for value in sorted(values)[:20]:
        print("   ", value)

    if len(values) > 20:
        print("    ...")


# ============================================================
# CHECK REDACTION MARKERS
# ============================================================

print()
print("MARKER INTEGRITY CHECK")
print("-" * 80)

for pii_type, marker in REDACTION_MARKERS.items():

    count = marker_counts[pii_type]

    if count > 0:
        print(f"[PASS] {marker} -> {count}")

    else:
        print(f"[INFO] {marker} -> 0")


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 80)

if remaining_total == 0:

    print("PHASE 12 STATUS: PASSED")

    print()
    print("No supported PII detector found remaining PII")
    print("in the generated redacted document.")

else:

    print("PHASE 12 STATUS: REVIEW REQUIRED")

    print()
    print(
        "Some PII detectors still found values in the "
        "redacted document."
    )

print("=" * 80)