from dob_detector import detect_dobs


TEST_CASES = [
    # Valid DOB formats
    "Date of Birth: 15/08/2000",
    "DOB: 21-04-1999",
    "D.O.B: 05/12/2001",
    "Birth Date: 7 July 2000",
    "Born: July 7, 2000",

    # Should NOT be detected
    "Date of Prospectus: 26 November 2025",
    "Company incorporated on July 30, 1979",
    "Offer opens on 15/12/2025",
    "Financial year ended 31/03/2025",
]


for text in TEST_CASES:

    result = detect_dobs(text)

    print(f"\nInput: {text}")
    print(f"Detected: {result}")
