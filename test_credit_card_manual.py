from credit_card_detector import detect_credit_cards


TEST_CASES = [
    # Valid Luhn test numbers
    "Card: 4111 1111 1111 1111",
    "Card: 5555 5555 5555 4444",
    "Card: 3782 822463 10005",

    # Invalid number
    "Invalid: 4111 1111 1111 1112",

    # Random long numbers
    "Year/reference: 2022080340",
    "Random: 3056306598953992176144951230793178014",
]


for text in TEST_CASES:

    result = detect_credit_cards(text)

    print(f"\nInput: {text}")
    print(f"Detected: {result}")
