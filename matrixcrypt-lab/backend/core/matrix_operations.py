"""Exact integer matrix arithmetic modulo 26 for the 2×2 Hill cipher.

Floating-point inversion is not used. Every product and inverse is an integer
reduced with the modulus.
"""

from math import gcd

MODULUS = 26


class MatrixError(ValueError):
    """A matrix is malformed or not invertible modulo 26."""


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_2x2(matrix: object) -> list[list[int]]:
    """Return a 2×2 integer matrix with entries reduced into 0..25."""
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 2:
        raise MatrixError("Key must be a 2×2 matrix: two rows of two integers.")
    reduced: list[list[int]] = []
    for row_index, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise MatrixError(
                f"Row {row_index} must contain exactly two integers."
            )
        reduced_row: list[int] = []
        for column_index, entry in enumerate(row):
            if not _is_int(entry):
                raise MatrixError(
                    f"Entry ({row_index}, {column_index}) must be an integer, "
                    f"got {entry!r}."
                )
            reduced_row.append(int(entry) % MODULUS)
        reduced.append(reduced_row)
    return reduced


def matrix_determinant(matrix: object) -> int:
    """Exact determinant of a 2×2 integer matrix, ad - bc.

    The result is not reduced modulo 26. Callers that need the residue use
    ``determinant % 26``.
    """
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 2:
        raise MatrixError("Determinant requires a 2×2 matrix of integers.")
    rows: list[list[int]] = []
    for row_index, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise MatrixError(
                f"Row {row_index} must contain exactly two integers."
            )
        exact_row: list[int] = []
        for column_index, entry in enumerate(row):
            if not _is_int(entry):
                raise MatrixError(
                    f"Entry ({row_index}, {column_index}) must be an integer, "
                    f"got {entry!r}."
                )
            exact_row.append(int(entry))
        rows.append(exact_row)
    a, b = rows[0]
    c, d = rows[1]
    return a * d - b * c


def modular_inverse(value: int, modulus: int = MODULUS) -> int:
    """Return x in 0..modulus-1 such that (value * x) % modulus == 1."""
    if not _is_int(value) or not _is_int(modulus):
        raise MatrixError("Modular inverse requires integer value and modulus.")
    if modulus <= 1:
        raise MatrixError("Modulus must be an integer greater than 1.")
    residue = int(value) % int(modulus)
    divisor = gcd(residue, int(modulus))
    if divisor != 1:
        raise MatrixError(
            f"No modular inverse exists: gcd({residue}, {modulus}) = {divisor}, "
            "which is not 1."
        )
    return pow(residue, -1, int(modulus))


def matrix_inverse_mod26(matrix: object) -> list[list[int]]:
    """Inverse of a 2×2 matrix modulo 26, using the adjugate formula.

    For K = [[a, b], [c, d]] with det = ad - bc and di = det^{-1} (mod 26):

        K^{-1} = di * [[d, -b], [-c, a]]  (mod 26)
    """
    reduced = _require_2x2(matrix)
    a, b = reduced[0]
    c, d = reduced[1]
    determinant = (a * d - b * c) % MODULUS
    inverse_det = modular_inverse(determinant, MODULUS)
    return [
        [(inverse_det * d) % MODULUS, (inverse_det * -b) % MODULUS],
        [(inverse_det * -c) % MODULUS, (inverse_det * a) % MODULUS],
    ]


def multiply_matrix_vector_mod26(
    matrix: object, vector: object
) -> list[int]:
    """Column-vector product (matrix × vector) modulo 26.

    result[i] = (sum_j matrix[i][j] * vector[j]) mod 26.
    """
    reduced = _require_2x2(matrix)
    if not isinstance(vector, (list, tuple)) or len(vector) != 2:
        raise MatrixError("Vector must contain exactly two integers.")
    entries: list[int] = []
    for index, entry in enumerate(vector):
        if not _is_int(entry):
            raise MatrixError(f"Vector entry {index} must be an integer, got {entry!r}.")
        entries.append(int(entry))
    return [
        (reduced[row][0] * entries[0] + reduced[row][1] * entries[1]) % MODULUS
        for row in range(2)
    ]


def multiply_matrices_mod26(left: object, right: object) -> list[list[int]]:
    """Product of two 2×2 matrices modulo 26."""
    left_matrix = _require_2x2(left)
    right_matrix = _require_2x2(right)
    product: list[list[int]] = []
    for row in range(2):
        product.append(
            [
                (
                    left_matrix[row][0] * right_matrix[0][col]
                    + left_matrix[row][1] * right_matrix[1][col]
                )
                % MODULUS
                for col in range(2)
            ]
        )
    return product
