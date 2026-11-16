# Cryptography and Matrices

MatrixCrypt Lab is a Python implementation of the classical 2×2 Hill cipher
with exact matrix arithmetic modulo 26 and structured, step-by-step explanations.
The current project contains the calculation library and its tests.

## Features

- Encrypt and decrypt letter pairs with a default or custom invertible key.
- Validate keys using the determinant and its modular inverse.
- Compute matrix products and inverses using integer arithmetic.
- Explain each block calculation and the inverse-key calculation as plain data.
- Record normalization and padding; preserve trailing X characters on decryption.

## Setup and tests

Use Python 3.10 or newer. From the repository root:

```sh
cd matrixcrypt-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

The library uses the Python standard library; pytest is required for the tests.

## Example

Run Python from `matrixcrypt-lab`:

```python
from backend.core.hill_cipher import encrypt, decrypt
from backend.core.explanation_engine import explain_encryption

encrypted = encrypt("HELP")
print(encrypted["ciphertext"])                  # HIAT
print(decrypt(encrypted["ciphertext"])["plaintext"])  # HELP
print(explain_encryption("HI")["blocks"])
```

The default key is `[[3, 3], [2, 5]]`. Letters map to A=0 through Z=25,
and encryption multiplies the key by each two-letter column vector modulo 26.
An odd number of letters is padded with X.

## Project layout

- `matrixcrypt-lab/backend/core/matrix_operations.py`: exact matrix arithmetic.
- `matrixcrypt-lab/backend/core/hill_cipher.py`: validation, encryption and decryption.
- `matrixcrypt-lab/backend/core/explanation_engine.py`: calculated explanations.
- `matrixcrypt-lab/tests/`: matrix, cipher and explanation tests.

The Hill cipher is a historical teaching cipher, unsuitable for protecting real secrets.
