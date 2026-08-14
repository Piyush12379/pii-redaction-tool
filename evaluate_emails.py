from email_detector import detect_emails
from email_ground_truth import TRUE_EMAILS
from extract_text import extract_document_text


def normalize(email):
    return email.strip().lower()


# --------------------------------------------------
# Extract document text
# --------------------------------------------------

blocks = extract_document_text("Prospectus.docx")

text = "\n".join(blocks)


# --------------------------------------------------
# Detect emails
# --------------------------------------------------

detected = detect_emails(text)


detected_normalized = {
    normalize(email)
    for email in detected
}


ground_truth = {
    normalize(email)
    for email in TRUE_EMAILS
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

for email in sorted(true_positives):
    print(email)


print("\n--- FALSE POSITIVES ---")

for email in sorted(false_positives):
    print(email)


print("\n--- FALSE NEGATIVES ---")

for email in sorted(false_negatives):
    print(email)
