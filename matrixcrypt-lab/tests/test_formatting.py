import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.hill_cipher import normalize_text

client = TestClient(app)


@pytest.mark.parametrize('text,expected', [
    ('Hello world!', 'HELLO WORLD!'),
    ('  Hi,\tOK!\nGo?  ', '  HI,\tOK!\nGO?  '),
    ('HI  OK', 'HI  OK'),
    ('Hi ßé😀 OK', 'HI ßé😀 OK'),
    ('cat!', 'CAT!X'),
    ('box!', 'BOX!X'),
    ('boxx!', 'BOXX!'),
    ('Hi, 42!', 'HI, 42!'),
])
def test_formatted_ciphertext_carries_its_own_layout(text, expected):
    request = {'text': text, 'operation': 'encrypt', 'preserve_formatting': True}
    response = client.post('/api/cipher', json=request)
    assert response.status_code == 200
    encrypted = response.json()
    assert normalize_text(encrypted['display_output']) == encrypted['ciphertext']
    assert ''.join(b['result_block'] for b in encrypted['blocks']) == encrypted['ciphertext']
    # No original plaintext, metadata, browser session, or server state required.
    decrypted = client.post('/api/cipher', json={
        'text': encrypted['display_output'], 'operation': 'decrypt',
        'preserve_formatting': True,
    }).json()
    assert decrypted['display_output'] == expected
    assert decrypted['plaintext'] == encrypted['padded_plaintext']


def test_opt_out_and_legacy_ciphertext_do_not_guess_word_boundaries():
    result = client.post('/api/cipher', json={'text': 'HELLO WORLD!'}).json()
    assert result['display_output'] == result['ciphertext']
    assert not result['preserve_formatting']
    decrypted = client.post('/api/cipher', json={
        'text': result['ciphertext'], 'operation': 'decrypt', 'preserve_formatting': True,
    }).json()
    assert decrypted['display_output'] == 'HELLOWORLD'


def test_maximum_formatted_output_can_be_decrypted_without_truncation():
    text = 'A' * 1999 + '!'
    encrypted = client.post('/api/cipher', json={'text': text, 'preserve_formatting': True}).json()
    assert len(encrypted['display_output']) == 2001
    response = client.post('/api/cipher', json={
        'text': encrypted['display_output'], 'operation': 'decrypt', 'preserve_formatting': True,
    })
    assert response.status_code == 200
    assert response.json()['display_output'] == text + 'X'


@pytest.mark.parametrize('body', [
    {'text': 'HI', 'preserve_formatting': 'true'},
    {'text': 'HI', 'preserve_formatting': 1},
    {'text': '!? 😀', 'preserve_formatting': True},
    {'text': 'A B C', 'operation': 'decrypt', 'preserve_formatting': True},
    {'text': 'A' * 2001, 'operation': 'encrypt'},
    {'text': 'A' * 2002, 'operation': 'decrypt'},
])
def test_formatting_does_not_bypass_validation(body):
    assert client.post('/api/cipher', json=body).status_code == 422
