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


def remove_one_padding_x(display_text: str) -> str:
    """Remove the last ASCII letter only when it is X; keep all separators.

    This is an explicit user assumption, never automatic padding detection.
    """
    for index in range(len(display_text) - 1, -1, -1):
        character = display_text[index]
        if character.isascii() and character.isalpha():
            if character != "X":
                break
            return display_text[:index] + display_text[index + 1:]
    raise CipherError("The decrypted message does not end in X. Turn off 'Remove one padding X' and decrypt again.")
