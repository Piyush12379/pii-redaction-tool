from extract_text import extract_document_text
from address_detector import detect_addresses


blocks = extract_document_text("Prospectus.docx")

addresses = set()

for block in blocks:

    detected = detect_addresses(block)

    for address in detected:
        addresses.add(address)


print("Addresses found:", len(addresses))

print("\n--- ADDRESSES ---")

for address in sorted(addresses):
    print(address)
