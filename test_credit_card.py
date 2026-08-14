from extract_text import extract_document_text
from credit_card_detector import detect_credit_cards


blocks = extract_document_text("Prospectus.docx")

all_cards = []

for block in blocks:

    cards = detect_credit_cards(block)

    for card in cards:

        if card not in all_cards:
            all_cards.append(card)


print("Credit cards found:", len(all_cards))

print("\nDetected credit cards:")

for card in all_cards:
    print(card)