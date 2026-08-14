from phone_detector import detect_phone_numbers
from phone_ground_truth import TRUE_PHONES
from extract_text import extract_document_text


def normalize_phone(phone):
    """
    Normalize phone numbers by keeping digits only.

    Example:
        +91 22 4009 4400
        +91 22 40094400

    both become:

        912240094400
    """

    return "".join(
        char for char in phone
        if char.isdigit()
    )


# --------------------------------------------------
# Extract prospectus text
# --------------------------------------------------

blocks = extract_document_text("Prospectus.docx")

text = "\n".join(blocks)


# --------------------------------------------------
# Detect phone numbers
# --------------------------------------------------

detected = detect_phone_numbers(text)


detected_normalized = {
    normalize_phone(phone)
    for phone in detected
}


ground_truth = {
    normalize_phone(phone)
    for phone in TRUE_PHONES
}


# --------------------------------------------------
# Calculate metrics
# --------------------------------------------------

true_positives = detected_normalized & ground_truth

false_positives = detected_normalized - ground_truth

false_negatives = ground_truth - detected_normalized


tp = len(true_positives)
fp = len(false_positives)
fn = len(false_negatives)


precision = (
    tp / (tp + fp)
    if (tp + fp) > 0
    else 0
)


recall = (
    tp / (tp + fn)
    if (tp + fn) > 0
    else 0
)


f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall) > 0
    else 0
)


# --------------------------------------------------
# Results
# --------------------------------------------------

print(f"TRUE POSITIVES: {tp}")
print(f"FALSE POSITIVES: {fp}")
print(f"FALSE NEGATIVES: {fn}")

print()

print(f"Precision: {precision * 100:.2f}%")
print(f"Recall: {recall * 100:.2f}%")
print(f"F1 Score: {f1 * 100:.2f}%")


print("\n--- TRUE POSITIVES ---")

for phone in sorted(true_positives):
    print(phone)


print("\n--- FALSE POSITIVES ---")

for phone in sorted(false_positives):
    print(phone)


print("\n--- FALSE NEGATIVES ---")

for phone in sorted(false_negatives):
    print(phone)
