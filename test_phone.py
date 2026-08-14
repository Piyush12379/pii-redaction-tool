from extract_text import extract_document_text
from phone_detector import detect_phone_numbers


blocks = extract_document_text("Prospectus.docx")

all_phones = []

for block in blocks:

    phones = detect_phone_numbers(block)

    for phone in phones:
        if phone not in all_phones:
            all_phones.append(phone)


print("Phone numbers found:", len(all_phones))

print("\nDetected phone numbers:")

for phone in all_phones:
    print(phone)
