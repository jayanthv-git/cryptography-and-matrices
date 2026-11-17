"""Keep non-alphabet characters outside the Hill cipher's A–Z calculation."""
from backend.core.hill_cipher import CipherError


def preserve_layout(source: str, transformed_letters: str) -> str:
    """Replace ASCII letter slots; retain separators verbatim and append padding.

    Layout is carried by the formatted ciphertext itself, so a recipient can
    decrypt it without hidden browser state or stored plaintext. Letter case is
    intentionally normalized. Non-A–Z characters remain unencrypted.
    """
    slots = sum(character.isascii() and character.isalpha() for character in source)
    if len(transformed_letters) not in (slots, slots + 1):
        raise CipherError("Transformed letters do not match the input layout.")
    letters = iter(transformed_letters)
    output = [
        next(letters) if character.isascii() and character.isalpha() else character
        for character in source
    ]
    return "".join(output) + "".join(letters)
