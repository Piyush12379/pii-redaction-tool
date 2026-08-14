from extract_text import extract_document_text

from pii_detector import (
    detect_document_pii,
    count_pii
)


# ============================================================
# EXTRACT DOCUMENT
# ============================================================

blocks = extract_document_text(
    "Prospectus.docx"
)


# ============================================================
# DETECT ALL PII
# ============================================================

results = detect_document_pii(
    blocks
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("=" * 80)
print("PII DETECTION REPORT")
print("=" * 80)


for category, values in results.items():

    print()
    print("-" * 80)
    print(category.upper())
    print("-" * 80)

    print("Count:", len(values))

    for value in values:
        print(value)


# ============================================================
# TOTAL
# ============================================================

print()
print("=" * 80)
print("TOTAL UNIQUE PII DETECTED:", count_pii(results))
print("=" * 80)