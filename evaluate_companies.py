import re
import spacy

from extract_text import extract_document_text
from company_ground_truth import TRUE_COMPANIES
from company_detector import detect_companies


def normalize_company(name):
    """
    Normalize company names for case-insensitive evaluation.
    """

    name = name.strip()

    # Remove footnote markers.
    name = re.sub(r'[*^&]+$', '', name)

    # Normalize whitespace.
    name = re.sub(r'\s+', ' ', name)

    return name.lower().strip()


nlp = spacy.load("en_core_web_sm")

blocks = extract_document_text("Prospectus.docx")

predicted_companies = set()

for block in blocks:

    companies = detect_companies(block, nlp)

    for company in companies:
        predicted_companies.add(company)


predicted_normalized = {
    normalize_company(company)
    for company in predicted_companies
}

true_normalized = {
    normalize_company(company)
    for company in TRUE_COMPANIES
}


true_positives = predicted_normalized & true_normalized
false_positives = predicted_normalized - true_normalized
false_negatives = true_normalized - predicted_normalized


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


print("TRUE POSITIVES:", tp)
print("FALSE POSITIVES:", fp)
print("FALSE NEGATIVES:", fn)

print(f"\nPrecision: {precision * 100:.2f}%")
print(f"Recall: {recall * 100:.2f}%")


print("\n--- TRUE POSITIVES ---")

for company in sorted(true_positives):
    print(company)


print("\n--- FALSE POSITIVES ---")

for company in sorted(false_positives):
    print(company)


print("\n--- FALSE NEGATIVES ---")

for company in sorted(false_negatives):
    print(company)
