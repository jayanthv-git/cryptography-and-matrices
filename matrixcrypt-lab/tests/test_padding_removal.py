import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.hill_cipher import encrypt

client = TestClient(app)


@pytest.mark.parametrize('text', ['CAT', 'cat!', '  cat  \n\n', 'BOX', 'WHY IS EVERYONE ACTING SO DUMB\n\n'])
@pytest.mark.parametrize('preserve', [False, True])
def test_explicit_removal_keeps_calculations_and_original_layout(text, preserve):
    enc = client.post('/api/cipher', json={'text': text, 'preserve_formatting': preserve}).json()
    response = client.post('/api/cipher', json={
        'text': enc['display_output'], 'operation': 'decrypt',
        'preserve_formatting': preserve, 'remove_padding': True,
    })
    assert response.status_code == 200
    result = response.json()
    assert result['display_output'] == (text.upper() if preserve else enc['normalized'])
    assert result['plaintext'] == enc['padded_plaintext']
    assert ''.join(block['result_block'] for block in result['blocks']) == enc['padded_plaintext']
    assert result['padding_removed'] is True
    assert 'at your request' in result['padding_note']


def test_genuine_final_x_is_preserved_by_default():
    cipher = encrypt('MATRIX')['ciphertext']
    result = client.post('/api/cipher', json={'text': cipher, 'operation': 'decrypt'}).json()
    assert result['display_output'] == 'MATRIX'
    assert result['padding_removed'] is False


def test_only_one_x_removed_and_trailing_separators_kept():
    cipher = encrypt('BOXX')['ciphertext'] + '! \n😀'
    result = client.post('/api/cipher', json={
        'text': cipher, 'operation': 'decrypt', 'preserve_formatting': True, 'remove_padding': True,
    }).json()
    assert result['display_output'] == 'BOX! \n😀'
    assert result['plaintext'] == 'BOXX'


@pytest.mark.parametrize('body', [
    {'text': 'HI', 'remove_padding': True},
    {'text': 'TC', 'operation': 'decrypt', 'remove_padding': True},
    {'text': 'TC', 'operation': 'decrypt', 'remove_padding': 'true'},
    {'text': 'TC', 'operation': 'decrypt', 'remove_padding': 1},
])
def test_invalid_padding_requests_are_rejected(body):
    response = client.post('/api/cipher', json=body)
    assert response.status_code == 422
    assert 'error' in response.json()
