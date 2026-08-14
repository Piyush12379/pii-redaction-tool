import re


CARD_PATTERN = re.compile(
    r'(?<!\d)'
    r'(?:\d[ -]?){13,19}'
    r'(?!\d)'
)


def luhn_check(number):
    """
    Validate a numeric string using the Luhn checksum.
    """

    digits = [int(digit) for digit in number]

    checksum = 0
    parity = len(digits) % 2

    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2

            if digit > 9:
                digit -= 9

        checksum += digit

    return checksum % 10 == 0


def detect_credit_cards(text):
    """
    Detect likely credit-card numbers using
    regex candidate extraction + Luhn validation.
    """

    candidates = CARD_PATTERN.findall(text)

    cards = []

    for candidate in candidates:

        number = re.sub(r'[\s-]', '', candidate)

        if 13 <= len(number) <= 19 and luhn_check(number):
            cards.append(candidate.strip())

    return list(dict.fromkeys(cards))
