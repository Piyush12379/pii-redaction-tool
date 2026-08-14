from extract_text import extract_document_text
from dob_detector import detect_dobs


blocks = extract_document_text("Prospectus.docx")

all_dobs = []

for block in blocks:

    dobs = detect_dobs(block)

    for dob in dobs:
        if dob not in all_dobs:
            all_dobs.append(dob)


print("DOBs found:", len(all_dobs))

print("\nDetected DOBs:")

for dob in all_dobs:
    print(dob)