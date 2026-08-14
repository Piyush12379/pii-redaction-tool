from extract_text import extract_document_text
from ssn_detector import detect_ssns


blocks = extract_document_text("Prospectus.docx")

all_ssns = []

for block in blocks:

    ssns = detect_ssns(block)

    for ssn in ssns:
        if ssn not in all_ssns:
            all_ssns.append(ssn)


print("SSNs found:", len(all_ssns))

print("\nDetected SSNs:")

for ssn in all_ssns:
    print(ssn)