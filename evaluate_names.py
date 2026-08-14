import spacy

from extract_text import extract_document_text
from name_ground_truth import TRUE_PERSONS
from name_detector import detect_persons


# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Extract document text
blocks = extract_document_text("Prospectus.docx")

predicted_persons = set()

# Run our actual name detector
for block in blocks:

    persons = detect_persons(block, nlp)

    for person in persons:
        predicted_persons.add(person.strip())


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

true_positives = predicted_persons & TRUE_PERSONS
false_positives = predicted_persons - TRUE_PERSONS
false_negatives = TRUE_PERSONS - predicted_persons


print("TRUE POSITIVES:", len(true_positives))
print("FALSE POSITIVES:", len(false_positives))
print("FALSE NEGATIVES:", len(false_negatives))


# ---------------------------------------------------------
# Precision / Recall / F1
# ---------------------------------------------------------

tp = len(true_positives)
fp = len(false_positives)
fn = len(false_negatives)

precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0

if precision + recall:
    f1 = 2 * precision * recall / (precision + recall)
else:
    f1 = 0


print(f"\nPrecision: {precision * 100:.2f}%")
print(f"Recall: {recall * 100:.2f}%")
print(f"F1 Score: {f1 * 100:.2f}%")


# ---------------------------------------------------------
# Details
# ---------------------------------------------------------

print("\n--- TRUE POSITIVES ---")

for name in sorted(true_positives):
    print(name)


print("\n--- FALSE POSITIVES ---")

for name in sorted(false_positives):
    print(name)


print("\n--- FALSE NEGATIVES ---")

for name in sorted(false_negatives):
    print(name)