"""Bounded, reproducible round-trip experiments; no security inference."""
import random
import string
from collections import Counter
from backend.core.hill_cipher import CipherError, encrypt, decrypt


def run_experiments(mode: str, plaintext: str, key: list[list[int]], count: int, seed: int, length: int) -> dict:
    if type(count) is not int or not 1 <= count <= 100:
        raise CipherError("Experiment count must be an integer from 1 to 100.")
    if type(length) is not int or not 1 <= length <= 200:
        raise CipherError("Generated message length must be an integer from 1 to 200.")
    if mode not in ("fixed", "generated"):
        raise CipherError("Choose fixed or generated messages.")
    if type(seed) is not int:
        raise CipherError("Seed must be an integer.")
    if not isinstance(plaintext, str) or len(plaintext) > 200:
        raise CipherError("Plaintext must be a string of at most 200 characters.")
    rng = random.Random(seed)
    rows = []
    pcounts, ccounts = Counter(), Counter()
    for index in range(count):
        source = plaintext if mode == "fixed" else "".join(rng.choice(string.ascii_uppercase) for _ in range(length))
        result = encrypt(source, key)
        recovered = decrypt(result["ciphertext"], key)["plaintext"]
        rows.append({"id": index + 1, "plaintext": source, "normalized": result["normalized"],
                     "padded_plaintext": result["padded_plaintext"], "key": result["key"],
                     "ciphertext": result["ciphertext"], "recovered": recovered,
                     "verified": recovered == result["padded_plaintext"]})
        pcounts.update(result["padded_plaintext"])
        ccounts.update(result["ciphertext"])
    success = sum(row["verified"] for row in rows)
    return {"mode": mode, "seed": seed, "completed": len(rows), "successful": success,
            "failed": len(rows) - success, "rows": rows,
            "plaintext_frequency": {c: pcounts[c] for c in string.ascii_uppercase},
            "ciphertext_frequency": {c: ccounts[c] for c in string.ascii_uppercase}}
