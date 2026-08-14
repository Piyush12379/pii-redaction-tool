import spacy

from extract_text import extract_document_text
from company_detector import detect_companies


nlp = spacy.load("en_core_web_sm")

blocks = extract_document_text("Prospectus.docx")

companies = set()

for block in blocks:

    detected = detect_companies(block, nlp)

    for company in detected:
        companies.add(company)


print("Companies found:", len(companies))

print("\n--- COMPANY NAMES ---")

for company in sorted(companies):
    print(company)
