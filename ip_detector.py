import re
import ipaddress


IP_PATTERN = re.compile(
    r'(?<![\w.])'
    r'(?:\d{1,3}\.){3}\d{1,3}'
    r'(?![\w.])'
)


def is_valid_ipv4(value):
    """
    Check whether a value is a valid IPv4 address.
    """

    try:
        ipaddress.IPv4Address(value)
        return True

    except ValueError:
        return False


def detect_ip_addresses(text):
    """
    Detect valid IPv4 addresses from text.
    """

    candidates = IP_PATTERN.findall(text)

    ips = []

    for candidate in candidates:

        if is_valid_ipv4(candidate):
            ips.append(candidate)

    return list(dict.fromkeys(ips))