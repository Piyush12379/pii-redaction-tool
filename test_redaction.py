from extract_text import extract_document_text

from pii_detector import detect_all_pii
from redaction_engine import redact_text


# ============================================================
# TEST TEXT
# ============================================================

test_text = """
Contact Person: Sarthak Malvadkar.
Email: cs.connect@kshinternational.com.
Telephone: +91 22 40094400.

KSH International Limited is the company.
Kushal Subbayya Hegde is a promoter.
"""


# ============================================================
# DETECT PII
# ============================================================

pii_results = detect_all_pii(
    test_text
)


# ============================================================
# SHOW DETECTIONS
# ============================================================

print("=" * 80)
print("DETECTED PII")
print("=" * 80)

for category, values in pii_results.items():

    print()
    print(category.upper())

    for value in values:
        print("  ", value)


# ============================================================
# REDACT
# ============================================================

redacted_text = redact_text(
    test_text,
    pii_results
)


# ============================================================
# SHOW ORIGINAL
# ============================================================

print()
print("=" * 80)
print("ORIGINAL TEXT")
print("=" * 80)

print(test_text)


# ============================================================
# SHOW REDACTED
# ============================================================

print()
print("=" * 80)
print("REDACTED TEXT")
print("=" * 80)

print(redacted_text)
