import spacy

from extract_text import extract_document_text
from company_detector import detect_companies


nlp = spacy.load("en_core_web_sm")

blocks = extract_document_text("Prospectus.docx")

# These are the current false positives.
FALSE_POSITIVES = {
    "Abhimanshree Society",
    "Advisory Private Limited",
    "Al-Ahleia Switchgear Co.",
    "Annapurna Family Trust",
    "AoA/Articles of Association or",
    "Broad Family Trust",
    "BSE Limited",
    "Corporation",
    "Deccan Gymkhana Society",
    "Dhaulagiri Family Trust",
    "Electricals Private Limited",
    "Everest Family Trust",
    "Export-Import Bank of India",
    "Kanchenjunga Family Trust",
    "Kanj & Co.",
    "LLP",
    "Makalu Family Trust",
    "National Payments Corporation",
    "Park IV Private Limited",
    "Solar Energy Corporation",
    "The BSE Limited",
    "The Federal Bank Limited",
}


for block in blocks:

    detected = detect_companies(block, nlp)

    for company in detected:

        if company.lower() in {
            fp.lower() for fp in FALSE_POSITIVES
        }:

            print("\n" + "=" * 80)
            print("FALSE POSITIVE:", company)
            print("=" * 80)
            print(block)
