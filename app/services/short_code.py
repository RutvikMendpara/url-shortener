import string

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(BASE62_ALPHABET)


def encode_base62(num: int) -> str:
    """Convert integer ID to Base62 string"""
    if num == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        encoded.append(BASE62_ALPHABET[remainder])
    return ''.join(reversed(encoded))