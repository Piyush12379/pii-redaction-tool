import re
import spacy

from extract_text import extract_document_text
from name_ground_truth import TRUE_PERSONS
from name_detector import detect_persons


def normalize_name(name):
    """
    Normalize a name for case-insensitive evaluation.
    """

    name = name.strip()

    # Remove common formatting markers.
    name = re.sub(r'[*^&]+', '', name)

    # Normalize multiple spaces.
    name = re.sub(r'\s+', ' ', name)

    # Case-insensitive comparison.
    return name.lower().strip()


# Load spaCy NER model.
nlp = spacy.load("en_core_web_sm")


# Read the actual assignment document.
blocks = extract_document_text("Prospectus.docx")


# Detect people from the document.
predicted_persons = set()

for block in blocks:

    persons = detect_persons(block, nlp)

    for person in persons:
        predicted_persons.add(person)


# Normalize predictions and ground truth
# so capitalization and formatting do not create false differences.
predicted_normalized = {
    normalize_name(name)
    for name in predicted_persons
}

true_normalized = {
    normalize_name(name)
    for name in TRUE_PERSONS
}


# Calculate evaluation sets.
true_positives = predicted_normalized & true_normalized
false_positives = predicted_normalized - true_normalized
false_negatives = true_normalized - predicted_normalized


# Calculate metrics.
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


# Print results.
print("TRUE POSITIVES:", tp)
print("FALSE POSITIVES:", fp)
print("FALSE NEGATIVES:", fn)

print(f"\nPrecision: {precision * 100:.2f}%")
print(f"Recall: {recall * 100:.2f}%")


print("\n--- TRUE POSITIVES ---")

for name in sorted(true_positives):
    print(name)


print("\n--- FALSE POSITIVES ---")

for name in sorted(false_positives):
    print(name)


print("\n--- FALSE NEGATIVES ---")

for name in sorted(false_negatives):
    print(name)
