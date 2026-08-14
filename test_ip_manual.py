from ip_detector import detect_ip_addresses


TEST_CASES = [
    # Valid IPv4 addresses
    "Server IP: 192.168.1.1",
    "IP address: 8.8.8.8",
    "Host: 10.0.0.25",

    # Invalid IPv4 addresses
    "Invalid IP: 999.999.999.999",
    "Invalid IP: 192.168.1.999",
    "Invalid IP: 256.1.1.1",

    # Numbers that should NOT be detected
    "Year: 2025",
    "PIN: 410 501",
    "Phone: 022-68052182",
    "SEBI Registration: INM000013004",
    "Reference: 2022080340",
]


for text in TEST_CASES:

    result = detect_ip_addresses(text)

    print(f"\nInput: {text}")
    print(f"Detected: {result}")
