"""Classical 2×2 Hill cipher over the alphabet A=0 … Z=25.

Encryption is C = K P (mod 26) on column vectors of two letters.
Decryption is P = K^{-1} C (mod 26). Trailing padding letters are kept,
because a real message may end in X.
"""

from math import gcd

from backend.core.matrix_operations import (
    MODULUS,
    MatrixError,
    matrix_determinant,
    matrix_inverse_mod26,
    modular_inverse,
    multiply_matrix_vector_mod26,
)

DEFAULT_KEY: list[list[int]] = [[3, 3], [2, 5]]
BLOCK_SIZE = 2
PADDING_CHAR = "X"
PADDING_NUMBER = ord(PADDING_CHAR) - ord("A")


class CipherError(ValueError):
    """Plaintext, ciphertext, or key failed validation."""


def _require_text(text: object, label: str) -> str:
    if not isinstance(text, str):
        raise CipherError(f"{label} must be a string.")
    return text


def _split_letters(text: str) -> tuple[str, str]:
    kept: list[str] = []
    removed: list[str] = []
    for character in text:
        upper = character.upper()
        if "A" <= upper <= "Z":
            kept.append(upper)
        else:
            removed.append(character)
    return "".join(kept), "".join(removed)


def normalize_text(text: str) -> str:
    """Uppercase A–Z letters only. Spaces and other characters are removed."""
    raw = _require_text(text, "Text")
    normalized, _removed = _split_letters(raw)
    return normalized


def text_to_numbers(text: str) -> list[int]:
    """Map A–Z letters to 0–25. Case is ignored. Other characters are rejected."""
    raw = _require_text(text, "Text")
    numbers: list[int] = []
    for index, character in enumerate(raw):
        upper = character.upper()
        if not ("A" <= upper <= "Z"):
            raise CipherError(
                f"Character {character!r} at position {index} is not a letter A–Z. "
                "Normalize the text before converting it to numbers."
            )
        numbers.append(ord(upper) - ord("A"))
    return numbers


def numbers_to_text(numbers: list[int]) -> str:
    """Map integers to A–Z. Each value is reduced modulo 26."""
    if isinstance(numbers, str) or not isinstance(numbers, (list, tuple)):
        raise CipherError("Numbers must be a list of integers.")
    letters: list[str] = []
    for index, value in enumerate(numbers):
        if isinstance(value, bool) or not isinstance(value, int):
            raise CipherError(f"Number at position {index} must be an integer, got {value!r}.")
        letters.append(chr((value % MODULUS) + ord("A")))
    return "".join(letters)


def validate_key(key: object) -> dict:
    """Check that a 2×2 integer matrix is invertible modulo 26.

    Malformed matrices raise CipherError. A well-formed matrix that shares a
    factor with 26 is returned with valid=False and a written explanation.
    """
    try:
        determinant = matrix_determinant(key)
    except MatrixError as error:
        raise CipherError(str(error)) from error

    determinant_mod = determinant % MODULUS
    shared_factor = gcd(determinant_mod, MODULUS)
    if shared_factor != 1:
        return {
            "valid": False,
            "determinant": determinant,
            "determinant_mod26": determinant_mod,
            "gcd": shared_factor,
            "modular_inverse_of_determinant": None,
            "inverse": None,
            "explanation": (
                f"The key is not invertible modulo {MODULUS} because "
                f"gcd({determinant_mod}, {MODULUS}) = {shared_factor}, which is not 1. "
                "A modular inverse of the determinant does not exist, so this matrix "
                "cannot be used as a Hill cipher key."
            ),
        }

    try:
        inverse_determinant = modular_inverse(determinant_mod, MODULUS)
        inverse = matrix_inverse_mod26(key)
    except MatrixError as error:
        raise CipherError(str(error)) from error

    return {
        "valid": True,
        "determinant": determinant,
        "determinant_mod26": determinant_mod,
        "gcd": shared_factor,
        "modular_inverse_of_determinant": inverse_determinant,
        "inverse": inverse,
        "explanation": (
            f"The key is invertible modulo {MODULUS} because "
            f"gcd({determinant_mod}, {MODULUS}) = 1. "
            f"The modular inverse of the determinant is {inverse_determinant}."
        ),
    }


def pad_plaintext(text: str, block_size: int = BLOCK_SIZE) -> str:
    """Append X until the normalized letter string fills complete blocks.

    ``text`` must already contain only A–Z letters. The empty string is a
    complete block sequence and is returned unchanged.
    """
    raw = _require_text(text, "Text")
    if isinstance(block_size, bool) or not isinstance(block_size, int) or block_size < 1:
        raise CipherError("Block size must be a positive integer.")
    for index, character in enumerate(raw):
        if not ("A" <= character <= "Z"):
            raise CipherError(
                f"Cannot pad {character!r} at position {index}. "
                "Pad only an uppercase A–Z string."
            )
    remainder = len(raw) % block_size
    if remainder == 0:
        return raw
    return raw + (PADDING_CHAR * (block_size - remainder))


def _working_key(key: object) -> tuple[list[list[int]], dict]:
    report = validate_key(key)
    if not report["valid"]:
        raise CipherError(report["explanation"])
    # validate_key already proved the matrix is 2×2 integers. Reduce for arithmetic.
    reduced = [
        [int(entry) % MODULUS for entry in row]
        for row in key  # type: ignore[union-attr]
    ]
    return reduced, report


def _blocks(numbers: list[int], block_size: int) -> list[list[int]]:
    return [numbers[index : index + block_size] for index in range(0, len(numbers), block_size)]


def encrypt(plaintext: str, key: list[list[int]] | None = None) -> dict:
    """Encrypt plaintext with a 2×2 Hill cipher key.

    Letters are uppercased, non-letters are removed, and a final X is added
    when the letter count is odd. The returned dict keeps that record.
    """
    raw = _require_text(plaintext, "Plaintext")
    normalized, removed = _split_letters(raw)
    if normalized == "":
        raise CipherError(
            "Plaintext is empty after removing spaces and non-letter characters."
        )
    padded = pad_plaintext(normalized, BLOCK_SIZE)
    padding = padded[len(normalized) :]
    working_key, key_report = _working_key(DEFAULT_KEY if key is None else key)

    ciphertext_numbers: list[int] = []
    for block in _blocks(text_to_numbers(padded), BLOCK_SIZE):
        ciphertext_numbers.extend(multiply_matrix_vector_mod26(working_key, block))

    return {
        "original": raw,
        "normalized": normalized,
        "padded_plaintext": padded,
        "padding_added": padding,
        "padding_count": len(padding),
        "removed_characters": removed,
        "key": working_key,
        "determinant": key_report["determinant"],
        "ciphertext": numbers_to_text(ciphertext_numbers),
        "block_size": BLOCK_SIZE,
    }


def decrypt(ciphertext: str, key: list[list[int]] | None = None) -> dict:
    """Decrypt ciphertext. Trailing X padding is not removed."""
    raw = _require_text(ciphertext, "Ciphertext")
    normalized, removed = _split_letters(raw)
    if normalized == "":
        raise CipherError(
            "Ciphertext is empty after removing spaces and non-letter characters."
        )
    if len(normalized) % BLOCK_SIZE != 0:
        raise CipherError(
            f"Ciphertext length must be a multiple of the block size ({BLOCK_SIZE}). "
            f"Got {len(normalized)} letter(s) after normalization."
        )
    working_key, key_report = _working_key(DEFAULT_KEY if key is None else key)
    inverse = key_report["inverse"]

    plaintext_numbers: list[int] = []
    for block in _blocks(text_to_numbers(normalized), BLOCK_SIZE):
        plaintext_numbers.extend(multiply_matrix_vector_mod26(inverse, block))

    return {
        "ciphertext": raw,
        "normalized_ciphertext": normalized,
        "removed_characters": removed,
        "key": working_key,
        "inverse_key": inverse,
        "determinant": key_report["determinant"],
        "plaintext": numbers_to_text(plaintext_numbers),
        "block_size": BLOCK_SIZE,
    }
