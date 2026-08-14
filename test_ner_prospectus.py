import spacy

from extract_text import extract_document_text


nlp = spacy.load("en_core_web_sm")

blocks = extract_document_text("Prospectus.docx")

people = []
organizations = []

for block in blocks:

    doc = nlp(block)

    for entity in doc.ents:

        if entity.label_ == "PERSON":

            if entity.text not in people:
                people.append(entity.text)

        elif entity.label_ == "ORG":

            if entity.text not in organizations:
                organizations.append(entity.text)


print("People found:", len(people))

print("\n--- PEOPLE ---")

for person in people:
    print(person)


print("\nOrganizations found:", len(organizations))

print("\n--- ORGANIZATIONS ---")

for organization in organizations:
    print(organization)
