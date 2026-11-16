"""Structured, step-by-step Hill cipher calculations.

Returns plain data (numbers, matrices, and short expressions). Nothing here is
HTML, and no message is hardcoded: every figure is computed from the input
and the key.
"""

from backend.core.hill_cipher import (
    BLOCK_SIZE,
    DEFAULT_KEY,
    CipherError,
    decrypt,
    encrypt,
    numbers_to_text,
    text_to_numbers,
    validate_key,
)
from backend.core.matrix_operations import MODULUS

_TIMES = "×"


def _letter_pairs(text: str) -> list[dict]:
    numbers = text_to_numbers(text)
    return [
        {"letter": letter, "number": number}
        for letter, number in zip(text, numbers)
    ]


def _row_product(coefficients: list[int], vector: list[int]) -> dict:
    terms = []
    total = 0
    for coefficient, value in zip(coefficients, vector):
        product = coefficient * value
        terms.append(
            {"coefficient": coefficient, "value": value, "product": product}
        )
        total += product
    residue = total % MODULUS
    joined = " + ".join(
        f"{term['coefficient']} {_TIMES} {term['value']}" for term in terms
    )
    return {
        "terms": terms,
        "expression": f"({joined}) mod {MODULUS}",
        "sum": total,
        "modulus": MODULUS,
        "residue": residue,
        "letter": chr(residue + ord("A")),
    }


def _block_steps(source_block: str, matrix: list[list[int]]) -> dict:
    vector = text_to_numbers(source_block)
    rows = [_row_product(row, vector) for row in matrix]
    result_vector = [row["residue"] for row in rows]
    return {
        "source_block": source_block,
        "source_letters": _letter_pairs(source_block),
        "source_vector": vector,
        "matrix": matrix,
        "rows": rows,
        "result_vector": result_vector,
        "result_block": numbers_to_text(result_vector),
    }


def explain_inverse_key(key: list[list[int]] | None = None) -> dict:
    """Show how K^{-1} (mod 26) is obtained from the adjugate formula.

    A matrix that is not invertible is reported with valid=False. No inverse
    is invented. A malformed matrix raises CipherError.
    """
    supplied = DEFAULT_KEY if key is None else key
    report = validate_key(supplied)
    if not report["valid"]:
        return {
            "valid": False,
            "supplied_key": supplied,
            "determinant": report["determinant"],
            "determinant_mod26": report["determinant_mod26"],
            "gcd": report["gcd"],
            "inverse": None,
            "explanation": report["explanation"],
        }

    working = [[int(entry) % MODULUS for entry in row] for row in supplied]
    a, b = working[0]
    c, d = working[1]
    determinant = a * d - b * c
    determinant_mod = determinant % MODULUS
    inverse_det = report["modular_inverse_of_determinant"]
    adjugate = [[d, -b], [-c, a]]
    scaled = [
        [inverse_det * adjugate[row][col] for col in range(2)]
        for row in range(2)
    ]
    inverse = [
        [scaled[row][col] % MODULUS for col in range(2)]
        for row in range(2)
    ]
    if inverse != report["inverse"]:
        raise CipherError("Inverse explanation does not match the cipher engine.")

    return {
        "valid": True,
        "supplied_key": supplied,
        "key": working,
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "determinant_expression": f"({a} {_TIMES} {d}) - ({b} {_TIMES} {c})",
        "determinant": determinant,
        "determinant_mod26": determinant_mod,
        "gcd": report["gcd"],
        "inverse_of_determinant": inverse_det,
        "inverse_check": {
            "product": determinant_mod * inverse_det,
            "residue": (determinant_mod * inverse_det) % MODULUS,
        },
        "adjugate": adjugate,
        "scaled_before_modulo": scaled,
        "inverse": inverse,
        "explanation": report["explanation"],
    }


def explain_encryption(plaintext: str, key: list[list[int]] | None = None) -> dict:
    """Step-by-step encryption for every two-letter block."""
    result = encrypt(plaintext, key)
    blocks = []
    padded = result["padded_plaintext"]
    for index in range(0, len(padded), BLOCK_SIZE):
        block = _block_steps(padded[index : index + BLOCK_SIZE], result["key"])
        block["index"] = index // BLOCK_SIZE
        blocks.append(block)

    ciphertext = "".join(block["result_block"] for block in blocks)
    if ciphertext != result["ciphertext"]:
        raise CipherError("Encryption steps do not match the cipher engine.")

    return {
        "operation": "encrypt",
        "original": result["original"],
        "normalized": result["normalized"],
        "padded_plaintext": padded,
        "padding_added": result["padding_added"],
        "padding_count": result["padding_count"],
        "removed_characters": result["removed_characters"],
        "letter_map": _letter_pairs(padded),
        "key": result["key"],
        "blocks": blocks,
        "ciphertext": ciphertext,
    }


def explain_decryption(ciphertext: str, key: list[list[int]] | None = None) -> dict:
    """Step-by-step decryption, including the inverse-key calculation."""
    result = decrypt(ciphertext, key)
    inverse_steps = explain_inverse_key(result["key"])
    blocks = []
    normalized = result["normalized_ciphertext"]
    for index in range(0, len(normalized), BLOCK_SIZE):
        block = _block_steps(
            normalized[index : index + BLOCK_SIZE], result["inverse_key"]
        )
        block["index"] = index // BLOCK_SIZE
        blocks.append(block)

    plaintext = "".join(block["result_block"] for block in blocks)
    if plaintext != result["plaintext"]:
        raise CipherError("Decryption steps do not match the cipher engine.")

    return {
        "operation": "decrypt",
        "ciphertext": result["ciphertext"],
        "normalized_ciphertext": normalized,
        "removed_characters": result["removed_characters"],
        "letter_map": _letter_pairs(normalized),
        "key": result["key"],
        "inverse_key": result["inverse_key"],
        "inverse_steps": inverse_steps,
        "blocks": blocks,
        "plaintext": plaintext,
        "padding_note": (
            "Trailing X is not removed. A genuine message may end in X, "
            "and padding cannot be identified without extra metadata."
        ),
    }
