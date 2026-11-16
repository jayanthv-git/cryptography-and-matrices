"""Tests for exact 2×2 matrix arithmetic modulo 26."""

import pytest

from backend.core.matrix_operations import (
    MODULUS,
    MatrixError,
    matrix_determinant,
    matrix_inverse_mod26,
    modular_inverse,
    multiply_matrices_mod26,
    multiply_matrix_vector_mod26,
)

DEFAULT_KEY = [[3, 3], [2, 5]]
DEFAULT_INVERSE = [[15, 17], [20, 9]]
IDENTITY = [[1, 0], [0, 1]]


def test_default_determinant_is_nine():
    assert matrix_determinant(DEFAULT_KEY) == 9


def test_determinant_is_exact_for_larger_entries():
    assert matrix_determinant([[10, 4], [5, 3]]) == 10


def test_modular_inverse_of_nine_is_three():
    assert modular_inverse(9) == 3
    assert (9 * modular_inverse(9)) % MODULUS == 1


def test_modular_inverse_rejects_non_coprime_values():
    with pytest.raises(MatrixError, match="gcd"):
        modular_inverse(2)
    with pytest.raises(MatrixError, match="gcd"):
        modular_inverse(13)


def test_default_inverse_matches_brief():
    assert matrix_inverse_mod26(DEFAULT_KEY) == DEFAULT_INVERSE


def test_key_times_inverse_is_identity():
    assert multiply_matrices_mod26(DEFAULT_KEY, DEFAULT_INVERSE) == IDENTITY
    assert multiply_matrices_mod26(DEFAULT_INVERSE, DEFAULT_KEY) == IDENTITY


def test_hi_column_vector_matches_worked_example():
    assert multiply_matrix_vector_mod26(DEFAULT_KEY, [7, 8]) == [19, 2]


def test_inverse_recovers_plaintext_vector():
    ciphertext = multiply_matrix_vector_mod26(DEFAULT_KEY, [7, 8])
    assert multiply_matrix_vector_mod26(DEFAULT_INVERSE, ciphertext) == [7, 8]


def test_equivalent_entries_reduce_modulo_26():
    equivalent = [[3 + 26, 3 - 26], [2, 5 + 52]]
    assert matrix_inverse_mod26(equivalent) == DEFAULT_INVERSE
    assert multiply_matrix_vector_mod26(equivalent, [7, 8]) == [19, 2]


@pytest.mark.parametrize(
    "matrix",
    [
        [[1, 0], [0, 2]],
        [[1, 1], [1, 1]],
        [[2, 0], [0, 13]],
        [[4, 6], [2, 5]],
    ],
)
def test_non_invertible_matrices_are_rejected(matrix):
    with pytest.raises(MatrixError, match="gcd"):
        matrix_inverse_mod26(matrix)


@pytest.mark.parametrize(
    "matrix",
    [
        [[1, 2, 3], [4, 5, 6]],
        [[1, 2], [3]],
        [[1, 2]],
        [[1.5, 2], [3, 4]],
        [[True, 1], [0, 1]],
        "[[3, 3], [2, 5]]",
        None,
        [[3, 3], [2, "5"]],
    ],
)
def test_malformed_matrices_are_rejected(matrix):
    with pytest.raises(MatrixError):
        matrix_determinant(matrix)
    with pytest.raises(MatrixError):
        matrix_inverse_mod26(matrix)


def test_vector_must_match_matrix_width():
    with pytest.raises(MatrixError):
        multiply_matrix_vector_mod26(DEFAULT_KEY, [1, 2, 3])
    with pytest.raises(MatrixError):
        multiply_matrix_vector_mod26(DEFAULT_KEY, [1.0, 2])
