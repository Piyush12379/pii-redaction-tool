from extract_text import extract_document_text


CANDIDATES = [
    "Eric Bacha",
    "Kishan Rastogi",
    "Abhijit Diwan",
    "Karunakar Hegde",
    "Kushal Hegde",
    "Pushpa Hegde",
    "Rajesh Hegde",
    "Rohit Hegde",
    "Vijay Hegde",
]


blocks = extract_document_text("Prospectus.docx")


for candidate in CANDIDATES:

    print("\n" + "=" * 80)
    print("CANDIDATE:", candidate)
    print("=" * 80)

    found = False

    for block in blocks:

        if candidate.lower() in block.lower():

            found = True

            text = block.strip()

            # Show the complete text block containing the candidate.
            print(text)

            print("\n" + "-" * 80)

    if not found:
        print("NOT FOUND")
