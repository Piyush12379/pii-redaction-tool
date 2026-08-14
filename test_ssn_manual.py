from ssn_detector import detect_ssns


TEST_CASES = [
    # Standard SSN
    "SSN: 123-45-6789",

    # Another standard format
    "Social Security Number: 987-65-4321",

    # Invalid formatting
    "Invalid: 123456789",

    # Random financial/document number
    "Reference: 2022080340",

    # Number with wrong grouping
    "Invalid: 1234-56-7890",
]


for text in TEST_CASES:

    result = detect_ssns(text)

    print(f"\nInput: {text}")
    print(f"Detected: {result}")
