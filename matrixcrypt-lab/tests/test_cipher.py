"""Tests for the 2×2 Hill cipher, including the brief's verified examples."""

import pytest

from backend.core.hill_cipher import (
    DEFAULT_KEY,
    CipherError,
    decrypt,
    encrypt,
    normalize_text,
    numbers_to_text,
    pad_plaintext,
    text_to_numbers,
    validate_key,
)
from backend.core.matrix_operations import multiply_matrices_mod26

IDENTITY = [[1, 0], [0, 1]]

VERIFIED_EXAMPLES = [
    ("HI", "TC"),
    ("OK", "UA"),
    ("GO", "IE"),
    ("HELP", "HIAT"),
    ("MATRIX", "KYETPB"),
    ("CRYPTO", "FLNTVE"),
]


def test_normalize_text_keeps_letters_only():
    assert normalize_text("hi") == "HI"
    assert normalize_text("Hi There!") == "HITHERE"
    assert normalize_text("  H, I. ") == "HI"
    assert normalize_text("123") == ""
    assert normalize_text("") == ""


def test_letter_number_conversion():
    assert text_to_numbers("HI") == [7, 8]
    assert text_to_numbers("hi") == [7, 8]
    assert numbers_to_text([19, 2]) == "TC"
    assert numbers_to_text([26, -1]) == "AZ"
    with pytest.raises(CipherError):
        text_to_numbers("H I")
    with pytest.raises(CipherError):
        numbers_to_text([1, "2"])


def test_default_key_validation_matches_brief():
    report = validate_key(DEFAULT_KEY)
    assert report["valid"] is True
    assert report["determinant"] == 9
    assert report["determinant_mod26"] == 9
    assert report["gcd"] == 1
    assert report["modular_inverse_of_determinant"] == 3
    assert report["inverse"] == [[15, 17], [20, 9]]
    assert "gcd(9, 26) = 1" in report["explanation"]


@pytest.mark.parametrize(
    "key",
    [
        [[1, 0], [0, 2]],
        [[1, 1], [2, 2]],
        [[13, 0], [0, 1]],
    ],
)
def test_invalid_keys_are_explained_not_used(key):
    report = validate_key(key)
    assert report["valid"] is False
    assert report["inverse"] is None
    assert report["gcd"] != 1
    assert "not invertible" in report["explanation"]
    with pytest.raises(CipherError, match="not invertible"):
        encrypt("HI", key)


@pytest.mark.parametrize(
    "key",
    [
        [[1, 2, 3], [4, 5, 6]],
        [[3, 3], [2]],
        [[3.0, 3], [2, 5]],
        None,
        [[3, 3], [2, 5], [1, 0]],
    ],
)
def test_malformed_keys_raise(key):
    with pytest.raises(CipherError):
        validate_key(key)


@pytest.mark.parametrize("plaintext, ciphertext", VERIFIED_EXAMPLES)
def test_verified_examples_encrypt(plaintext, ciphertext):
    result = encrypt(plaintext)
    assert result["ciphertext"] == ciphertext
    assert result["key"] == DEFAULT_KEY
    assert result["padding_count"] == 0
    assert result["padded_plaintext"] == plaintext


@pytest.mark.parametrize("plaintext, ciphertext", VERIFIED_EXAMPLES)
def test_verified_examples_decrypt(plaintext, ciphertext):
    result = decrypt(ciphertext)
    assert result["plaintext"] == plaintext
    assert result["inverse_key"] == [[15, 17], [20, 9]]


def test_case_spaces_and_punctuation_do_not_change_ciphertext():
    expected = encrypt("HI")["ciphertext"]
    for variant in ("hi", "Hi", "H I", "H.I!", "  hi  "):
        result = encrypt(variant)
        assert result["normalized"] == "HI"
        assert result["ciphertext"] == expected


def test_odd_length_message_is_padded_with_x_and_padding_is_kept():
    result = encrypt("CAT")
    assert result["normalized"] == "CAT"
    assert result["padded_plaintext"] == "CATX"
    assert result["padding_added"] == "X"
    assert result["padding_count"] == 1
    assert result["ciphertext"] == "GEWX"
    recovered = decrypt(result["ciphertext"])
    assert recovered["plaintext"] == "CATX"


def test_legitimate_trailing_x_is_not_stripped():
    result = encrypt("AX")
    assert result["normalized"] == "AX"
    assert result["padding_count"] == 0
    assert decrypt(result["ciphertext"])["plaintext"] == "AX"


def test_repeated_characters_round_trip():
    result = encrypt("aaa")
    assert result["padded_plaintext"] == "AAAX"
    assert decrypt(result["ciphertext"])["plaintext"] == "AAAX"


def test_longer_message_with_punctuation_round_trip():
    message = "Cryptography and matrices!"
    result = encrypt(message)
    assert result["normalized"] == "CRYPTOGRAPHYANDMATRICES"
    assert result["removed_characters"] == "  !"
    assert len(result["padded_plaintext"]) % 2 == 0
    assert decrypt(result["ciphertext"])["plaintext"] == result["padded_plaintext"]


def test_empty_plaintext_and_ciphertext_are_rejected():
    with pytest.raises(CipherError, match="empty"):
        encrypt("")
    with pytest.raises(CipherError, match="empty"):
        encrypt("... ---")
    with pytest.raises(CipherError, match="empty"):
        decrypt("")
    with pytest.raises(CipherError, match="empty"):
        decrypt("123")


def test_odd_length_ciphertext_is_rejected():
    with pytest.raises(CipherError, match="block size"):
        decrypt("T")
    with pytest.raises(CipherError, match="block size"):
        decrypt("TCA")


def test_ciphertext_spaces_are_removed_before_length_check():
    assert decrypt("T C")["plaintext"] == "HI"
    assert decrypt("HI AT")["plaintext"] == "HELP"


def test_round_trip_for_every_verified_example():
    for plaintext, ciphertext in VERIFIED_EXAMPLES:
        encrypted = encrypt(plaintext)
        assert encrypted["ciphertext"] == ciphertext
        assert decrypt(encrypted["ciphertext"])["plaintext"] == plaintext


def test_valid_key_times_its_inverse_is_identity():
    report = validate_key(DEFAULT_KEY)
    assert multiply_matrices_mod26(DEFAULT_KEY, report["inverse"]) == IDENTITY


def test_custom_valid_key_round_trip():
    key = [[1, 1], [1, 2]]
    report = validate_key(key)
    assert report["valid"] is True
    result = encrypt("HELP", key)
    assert decrypt(result["ciphertext"], key)["plaintext"] == "HELP"


def test_pad_plaintext_rejects_unnormalized_text():
    assert pad_plaintext("HELP") == "HELP"
    assert pad_plaintext("A") == "AX"
    assert pad_plaintext("") == ""
    with pytest.raises(CipherError):
        pad_plaintext("hi")
