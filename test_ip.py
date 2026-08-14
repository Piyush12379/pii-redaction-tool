from extract_text import extract_document_text
from ip_detector import detect_ip_addresses


blocks = extract_document_text("Prospectus.docx")

all_ips = []

for block in blocks:

    ips = detect_ip_addresses(block)

    for ip in ips:
        if ip not in all_ips:
            all_ips.append(ip)


print("IP addresses found:", len(all_ips))

print("\nDetected IP addresses:")

for ip in all_ips:
    print(ip)
