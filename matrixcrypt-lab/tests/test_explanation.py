"""Tests that step-by-step explanations come from the input, not a fixed script."""

import pytest

from backend.core.explanation_engine import (
    explain_decryption,
    explain_encryption,
    explain_inverse_key,
)
from backend.core.hill_cipher import DEFAULT_KEY, CipherError, decrypt, encrypt

INVERSE = [[15, 17], [20, 9]]


def test_hi_encryption_matches_the_worked_example():
    steps = explain_encryption("HI")
    assert steps["original"] == "HI"
    assert steps["normalized"] == "HI"
    assert steps["letter_map"] == [
        {"letter": "H", "number": 7},
        {"letter": "I", "number": 8},
    ]
    assert steps["key"] == DEFAULT_KEY
    assert len(steps["blocks"]) == 1

    block = steps["blocks"][0]
    assert block["source_vector"] == [7, 8]
    first, second = block["rows"]
    assert first["expression"] == "(3 × 7 + 3 × 8) mod 26"
    assert first["sum"] == 45
    assert first["residue"] == 19
    assert first["letter"] == "T"
    assert second["expression"] == "(2 × 7 + 5 × 8) mod 26"
    assert second["sum"] == 54
    assert second["residue"] == 2
    assert second["letter"] == "C"
    assert block["result_block"] == "TC"
    assert steps["ciphertext"] == "TC"


def test_every_block_is_explained_for_help():
    steps = explain_encryption("HELP")
    assert [block["source_block"] for block in steps["blocks"]] == ["HE", "LP"]
    assert [block["result_block"] for block in steps["blocks"]] == ["HI", "AT"]
    assert steps["ciphertext"] == "HIAT"
    he = steps["blocks"][0]
    assert he["source_vector"] == [7, 4]
    assert he["rows"][0]["sum"] == 33
    assert he["rows"][0]["residue"] == 7
    lp = steps["blocks"][1]
    assert lp["source_vector"] == [11, 15]
    assert lp["rows"][1]["sum"] == 97
    assert lp["rows"][1]["letter"] == "T"


def test_steps_follow_a_different_message_and_key():
    key = [[1, 1], [1, 2]]
    steps = explain_encryption("ok", key)
    assert steps["normalized"] == "OK"
    assert steps["key"] == key
    block = steps["blocks"][0]
    assert block["source_vector"] == [14, 10]
    assert block["rows"][0]["expression"] == "(1 × 14 + 1 × 10) mod 26"
    assert block["rows"][0]["sum"] == 24
    assert block["rows"][1]["expression"] == "(1 × 14 + 2 × 10) mod 26"
    assert block["rows"][1]["sum"] == 34
    assert steps["ciphertext"] == encrypt("ok", key)["ciphertext"]


def test_padding_appears_as_its_own_letters_in_the_steps():
    steps = explain_encryption("cat!")
    assert steps["normalized"] == "CAT"
    assert steps["padded_plaintext"] == "CATX"
    assert steps["padding_added"] == "X"
    assert steps["removed_characters"] == "!"
    assert [block["source_block"] for block in steps["blocks"]] == ["CA", "TX"]
    assert steps["ciphertext"] == encrypt("cat!")["ciphertext"]


def test_inverse_explanation_matches_the_brief():
    steps = explain_inverse_key()
    assert steps["valid"] is True
    assert steps["determinant_expression"] == "(3 × 5) - (3 × 2)"
    assert steps["determinant"] == 9
    assert steps["gcd"] == 1
    assert steps["inverse_of_determinant"] == 3
    assert steps["inverse_check"] == {"product": 27, "residue": 1}
    assert steps["adjugate"] == [[5, -3], [-2, 3]]
    assert steps["scaled_before_modulo"] == [[15, -9], [-6, 9]]
    assert steps["inverse"] == INVERSE


def test_tc_decryption_uses_the_inverse_on_each_row():
    steps = explain_decryption("TC")
    assert steps["inverse_key"] == INVERSE
    assert steps["inverse_steps"]["inverse"] == INVERSE
    block = steps["blocks"][0]
    assert block["source_vector"] == [19, 2]
    assert block["matrix"] == INVERSE
    first, second = block["rows"]
    assert first["expression"] == "(15 × 19 + 17 × 2) mod 26"
    assert first["sum"] == 319
    assert first["residue"] == 7
    assert first["letter"] == "H"
    assert second["sum"] == 398
    assert second["residue"] == 8
    assert second["letter"] == "I"
    assert steps["plaintext"] == "HI"
    assert "Trailing X" in steps["padding_note"]


def test_decryption_steps_match_the_engine_for_every_example():
    for plaintext in ("HI", "OK", "GO", "HELP", "MATRIX", "CRYPTO", "CAT"):
        encrypted = encrypt(plaintext)
        steps = explain_decryption(encrypted["ciphertext"])
        assert steps["plaintext"] == decrypt(encrypted["ciphertext"])["plaintext"]
        assert steps["plaintext"] == encrypted["padded_plaintext"]


def test_invalid_key_does_not_invent_an_inverse():
    report = explain_inverse_key([[1, 0], [0, 2]])
    assert report["valid"] is False
    assert report["inverse"] is None
    assert report["gcd"] == 2
    with pytest.raises(CipherError):
        explain_encryption("HI", [[1, 0], [0, 2]])
    with pytest.raises(CipherError):
        explain_decryption("TC", [[1, 1], [1, 1]])


def test_empty_input_is_rejected():
    with pytest.raises(CipherError):
        explain_encryption("...")
    with pytest.raises(CipherError):
        explain_decryption("T")
