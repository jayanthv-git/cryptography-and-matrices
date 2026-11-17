import csv
import io
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.hill_cipher import CipherError, encrypt, normalize_text, text_to_numbers
from backend.core.cryptanalysis import recover_key, RecoveryError
from backend.core.experiments import run_experiments
from backend.core.survey import analyze_survey

client = TestClient(app)
KEY = [[3, 3], [2, 5]]
PAIRS = [{"plaintext": "HI", "ciphertext": "TC"}, {"plaintext": "LP", "ciphertext": "AT"}]

@pytest.mark.parametrize("text,expected", [("HI", "TC"), ("OK", "UA"), ("GO", "IE"), ("HELP", "HIAT"), ("MATRIX", "KYETPB"), ("CRYPTO", "FLNTVE"), ("CAT", "GEWX")])
def test_api_examples(text, expected):
    r = client.post('/api/cipher', json={"text": text, "key": KEY})
    assert r.status_code == 200
    data = r.json()
    assert data['ciphertext'] == expected
    assert ''.join(b['result_block'] for b in data['blocks']) == expected
    d = client.post('/api/cipher', json={"text": expected, "operation": "decrypt", "key": KEY}).json()
    assert d['plaintext'] == data['padded_plaintext']
    assert d['inverse_steps']['inverse'] == [[15, 17], [20, 9]]

@pytest.mark.parametrize('raw', ['ß', 'ﬃ', 'ı', 'é', '😀', 'Σ'])
def test_unicode_removed_without_expansion(raw):
    assert normalize_text('h' + raw + 'i') == 'HI'
    assert encrypt('h' + raw + 'i')['removed_characters'] == raw
    with pytest.raises(CipherError):
        text_to_numbers(raw)

@pytest.mark.parametrize('body', [
    {"text": ""}, {"text": "😀 ß"}, {"text": "ABC", "operation": "decrypt"},
    {"text": "HI", "key": [[True, 3], [2, 5]]},
    {"text": "HI", "key": [[3.1, 3], [2, 5]]},
    {"text": "HI", "key": [[3.0, 3], [2, 5]]},
    {"text": "HI", "key": [[3, 3]]},
    {"text": "HI", "key": [[2, 0], [0, 2]]},
    {"text": "HI", "key": [[10**12, 3], [2, 5]]},
    {"text": "a" * 2001}, {"text": "HI", "surprise": 1},
])
def test_validation(body):
    response = client.post('/api/cipher', json=body)
    assert response.status_code == 422
    assert set(response.json()['error']) == {'code', 'message', 'details'}

def test_key_report_and_calculations():
    assert client.post('/api/key/validate', json={'key': [[2, 0], [0, 2]]}).json()['valid'] is False
    block = client.post('/api/cipher', json={'text': 'HI'}).json()['blocks'][0]
    assert block['source_vector'] == [7, 8]
    assert [row['sum'] for row in block['rows']] == [45, 54]
    assert block['result_vector'] == [19, 2]

def test_recovery_and_later_usable_pair():
    assert recover_key(PAIRS)['key'] == KEY
    evidence = [{'plaintext': 'AA', 'ciphertext': 'AA'}, *PAIRS]
    result = recover_key(evidence)
    assert result['selected_pair_indices'] == [1, 2]
    assert all(v['matches'] for v in result['verification'])
    assert client.post('/api/recover', json={'pairs': evidence}).json()['key'] == KEY

@pytest.mark.parametrize('pairs,code', [
    (PAIRS[:1], 'insufficient_evidence'),
    ([{'plaintext': 'ßA', 'ciphertext': 'AA'}, PAIRS[0]], 'malformed_block'),
    ([{'plaintext': 'AA', 'ciphertext': 'AA'}, {'plaintext': 'BB', 'ciphertext': 'FF'}], 'method_undetermined'),
    (PAIRS + [{'plaintext': 'GO', 'ciphertext': 'AA'}], 'inconsistent_evidence'),
    ([{'plaintext': 'BA', 'ciphertext': 'CA'}, {'plaintext': 'AB', 'ciphertext': 'AC'}], 'invalid_recovered_key'),
])
def test_recovery_failures(pairs, code):
    with pytest.raises(RecoveryError) as error:
        recover_key(pairs)
    assert error.value.code == code

def test_experiments_reproducible_padding_and_accounting():
    args = dict(mode='generated', plaintext='', key=KEY, count=10, seed=42, length=7)
    result = run_experiments(**args)
    assert result == run_experiments(**args)
    assert result != run_experiments(**{**args, 'seed': 43})
    assert result['completed'] == result['successful'] == 10
    assert result['failed'] == 0
    assert sum(result['plaintext_frequency'].values()) == 80
    assert sum(result['ciphertext_frequency'].values()) == 80
    assert all(r['recovered'] == r['padded_plaintext'] for r in result['rows'])
    fixed = run_experiments(**{**args, 'mode': 'fixed', 'plaintext': 'cat!'})
    assert all(r['recovered'] == 'CATX' for r in fixed['rows'])
    assert client.post('/api/experiments', json=args).status_code == 200

@pytest.mark.parametrize('update', [{'count': 0}, {'count': 101}, {'count': True}, {'seed': 1.5}, {'length': 201}, {'mode': 'fixed', 'plaintext': '!!!'}])
def test_experiment_api_limits(update):
    assert client.post('/api/experiments', json=update).status_code == 422

def test_survey_missing_and_denominators():
    result = analyze_survey('\ufeffawareness,two_factor\nhigh,yes\nlow,\n,No\n\n')
    assert result['responses'] == 3
    assert result['skipped_empty_rows'] == 1
    field = result['fields'][0]
    assert field['answered'] == 2 and field['missing'] == 1
    assert field['categories'][-1] == {'label': 'high', 'count': 1, 'percentage': 50.0}
    assert client.post('/api/survey', json={'csv': 'awareness\nhigh\n'}).status_code == 200
    assert analyze_survey('awareness,two_factor\n,yes\n')['fields'][0]['answered'] == 0

@pytest.mark.parametrize('content', ['', 'awareness\n', 'name\nJane\n', 'awareness,awareness\nhigh,low\n', 'awareness\nmaybe\n', 'awareness\nhigh,low\n', 'awareness\n"high\n', 'awareness\n' + 'high\n' * 1001, 'x' * 1_048_577, 'awareness\n\x00'])
def test_survey_errors(content):
    with pytest.raises(CipherError):
        analyze_survey(content)

def test_template_and_error_format():
    response = client.get('/api/survey/template')
    assert response.status_code == 200 and 'attachment' in response.headers['content-disposition']
    assert len(list(csv.reader(io.StringIO(response.text)))) == 1
    assert 'error' in client.get('/api/missing').json()
    assert client.post('/api/survey', content='x'*1_100_001).status_code == 413
    assert client.post('/api/cipher', content='{bad', headers={'content-type':'application/json'}).json()['error']['code'] == 'validation_error'

def test_survey_surrogates_return_clear_error():
    with pytest.raises(CipherError, match='UTF-8'):
        analyze_survey('awareness\n\ud800\n')
    response = client.post('/api/survey', content='{"csv":"awareness\\n\\ud800\\n"}', headers={'content-type':'application/json'})
    assert response.status_code == 422
