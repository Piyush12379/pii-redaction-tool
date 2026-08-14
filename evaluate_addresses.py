from extract_text import extract_document_text
from address_detector import detect_addresses
from address_ground_truth import TRUE_ADDRESSES


def normalize_address(address):
    """
    Normalize an address for evaluation.
    """

    address = address.strip()

    # Normalize whitespace
    address = " ".join(address.split())

    # Case-insensitive comparison
    return address.lower()


# Normalize ground truth
TRUE_ADDRESSES_NORMALIZED = {
    normalize_address(address)
    for address in TRUE_ADDRESSES
}


blocks = extract_document_text("Prospectus.docx")

predicted_addresses = set()

for block in blocks:

    addresses = detect_addresses(block)

    for address in addresses:
        predicted_addresses.add(
            normalize_address(address)
        )


true_positives = (
    predicted_addresses
    & TRUE_ADDRESSES_NORMALIZED
)

false_positives = (
    predicted_addresses
    - TRUE_ADDRESSES_NORMALIZED
)

false_negatives = (
    TRUE_ADDRESSES_NORMALIZED
    - predicted_addresses
)


# Calculate precision
if len(predicted_addresses) > 0:
    precision = (
        len(true_positives)
        / len(predicted_addresses)
    ) * 100
else:
    precision = 0


# Calculate recall
if len(TRUE_ADDRESSES_NORMALIZED) > 0:
    recall = (
        len(true_positives)
        / len(TRUE_ADDRESSES_NORMALIZED)
    ) * 100
else:
    recall = 0


print("TRUE POSITIVES:", len(true_positives))
print("FALSE POSITIVES:", len(false_positives))
print("FALSE NEGATIVES:", len(false_negatives))

print(f"\nPrecision: {precision:.2f}%")
print(f"Recall: {recall:.2f}%")


print("\n--- TRUE POSITIVES ---")

for address in sorted(true_positives):
    print(address)


print("\n--- FALSE POSITIVES ---")

for address in sorted(false_positives):
    print(address)


print("\n--- FALSE NEGATIVES ---")

for address in sorted(false_negatives):
    print(address)
