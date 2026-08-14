from extract_text import extract_document_text

from pii_detector import detect_all_pii
from redaction_engine import redact_text


# ============================================================
# LOAD PROSPECTUS
# ============================================================

blocks = extract_document_text(
    "Prospectus.docx"
)


# ============================================================
# REDACT ALL BLOCKS
# ============================================================

redacted_blocks = []

total_replacements = 0


for block in blocks:

    pii_results = detect_all_pii(
        block
    )

    # Count detected values.
    for values in pii_results.values():
        total_replacements += len(values)

    redacted = redact_text(
        block,
        pii_results
    )

    redacted_blocks.append(
        redacted
    )


# ============================================================
# SAVE REDACTED TEXT
# ============================================================

with open(
    "redacted_prospectus.txt",
    "w",
    encoding="utf-8"
) as file:

    for block in redacted_blocks:

        file.write(
            block
        )

        file.write(
            "\n\n"
        )


# ============================================================
# RESULT
# ============================================================

print("=" * 80)
print("PHASE 10 REDACTION COMPLETE")
print("=" * 80)

print(
    "Document blocks:",
    len(blocks)
)

print(
    "Detected PII occurrences:",
    total_replacements
)

print()
print(
    "Output:",
    "redacted_prospectus.txt"
)
