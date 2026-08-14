import re
from extract_text import extract_document_text


pattern = r'[\w\.-]+@[\w\.-]+\.\w+'

blocks = extract_document_text("Prospectus.docx")

emails = []

for block in blocks:

    matches = re.findall(pattern, block)

    for email in matches:
        if email not in emails:
            emails.append(email)


print("Emails found:", len(emails))

print("\nDetected email addresses:")

for email in emails:
    print(email)