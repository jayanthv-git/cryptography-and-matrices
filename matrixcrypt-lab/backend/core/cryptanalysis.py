"""Known-plaintext recovery using two invertible plaintext columns."""
from itertools import combinations
import re

from backend.core.hill_cipher import CipherError, text_to_numbers, validate_key
from backend.core.matrix_operations import matrix_determinant, matrix_inverse_mod26, multiply_matrices_mod26


class RecoveryError(CipherError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def recover_key(pairs: list[dict]) -> dict:
    if not 2 <= len(pairs) <= 30:
        raise RecoveryError("insufficient_evidence", "Supply between 2 and 30 aligned two-letter pairs.")
    evidence = []
    for index, pair in enumerate(pairs):
        p, c = pair.get("plaintext"), pair.get("ciphertext")
        if not all(isinstance(v, str) and re.fullmatch(r"[A-Za-z]{2}", v) for v in (p, c)):
            raise RecoveryError("malformed_block", f"Pair {index + 1}: each block must contain exactly two ASCII letters A–Z, without spaces.")
        evidence.append({"plaintext": p.upper(), "ciphertext": c.upper()})
    for i, j in combinations(range(len(evidence)), 2):
        pcols = [text_to_numbers(evidence[k]["plaintext"]) for k in (i, j)]
        ccols = [text_to_numbers(evidence[k]["ciphertext"]) for k in (i, j)]
        p = [list(row) for row in zip(*pcols)]
        c = [list(row) for row in zip(*ccols)]
        if not validate_key(p)["valid"]:
            continue
        inverse = matrix_inverse_mod26(p)
        key = multiply_matrices_mod26(c, inverse)
        # An invertible P uniquely determines the linear map, even if K is singular.
        verification = []
        for pair in evidence:
            v = text_to_numbers(pair["plaintext"])
            actual = "".join(chr(sum(key[r][k] * v[k] for k in range(2)) % 26 + 65) for r in range(2))
            verification.append({**pair, "predicted": actual, "matches": actual == pair["ciphertext"]})
        if not all(item["matches"] for item in verification):
            raise RecoveryError("inconsistent_evidence", "No single linear Hill key matches all supplied pairs: the uniquely determined matrix contradicts additional evidence.")
        if not validate_key(key)["valid"]:
            raise RecoveryError("invalid_recovered_key", "The evidence uniquely determines a non-invertible matrix. No valid invertible Hill key matches these pairs.")
        products = [[sum(c[r][k] * inverse[k][col] for k in range(2)) for col in range(2)] for r in range(2)]
        return {"selected_pair_indices": [i, j], "plaintext_matrix": p, "ciphertext_matrix": c,
                "determinant": matrix_determinant(p), "determinant_mod26": matrix_determinant(p) % 26,
                "plaintext_inverse": inverse, "products": products, "key": key, "verification": verification}
    raise RecoveryError("method_undetermined", "This recovery method cannot determine a key from these pairs: no two plaintext columns form an invertible matrix modulo 26. This does not establish that no key exists. Try different independent plaintext blocks.")
