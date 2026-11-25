const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const message = document.querySelector('#message');
const inputs = [...document.querySelectorAll('.matrix-input')];
const output = document.querySelector('#output');
const detail = document.querySelector('#detail');
const error = document.querySelector('#error');
const keyStatus = document.querySelector('#key-status');

function mod(value, base = 26) { return ((value % base) + base) % base; }
function gcd(a, b) { while (b) [a, b] = [b, a % b]; return Math.abs(a); }
function clean(text) { return text.toUpperCase().replace(/[^A-Z]/g, ''); }
function key() { return inputs.map((input) => Number(input.value)); }
function inverse(matrix) {
  const [a, b, c, d] = matrix; const determinant = a * d - b * c; const reduced = mod(determinant);
  if (gcd(reduced, 26) !== 1) return null;
  const inverseDeterminant = [...Array(26).keys()].find((n) => mod(reduced * n) === 1);
  return [mod(d * inverseDeterminant), mod(-b * inverseDeterminant), mod(-c * inverseDeterminant), mod(a * inverseDeterminant)];
}
function validateKey(matrix) {
  if (matrix.some((value) => !Number.isInteger(value))) return 'Enter four whole numbers.';
  const determinant = matrix[0] * matrix[3] - matrix[1] * matrix[2];
  return gcd(mod(determinant), 26) === 1 ? `Valid key · determinant ${determinant} ≡ ${mod(determinant)} (mod 26)` : `Invalid key · determinant ${determinant} has no inverse mod 26`;
}
function transform(operation) {
  error.textContent = ''; const raw = clean(message.value); const matrix = key(); const status = validateKey(matrix);
  if (!status.startsWith('Valid')) { error.textContent = status; return; }
  if (!raw) { error.textContent = 'Enter at least one letter.'; return; }
  const working = operation === 'encrypt' && raw.length % 2 ? `${raw}X` : raw;
  if (operation === 'decrypt' && working.length % 2) { error.textContent = 'Ciphertext must contain an even number of letters.'; return; }
  const transformMatrix = operation === 'encrypt' ? matrix : inverse(matrix); let result = '';
  for (let index = 0; index < working.length; index += 2) {
    const x = alphabet.indexOf(working[index]); const y = alphabet.indexOf(working[index + 1]);
    result += alphabet[mod(transformMatrix[0] * x + transformMatrix[1] * y)];
    result += alphabet[mod(transformMatrix[2] * x + transformMatrix[3] * y)];
  }
  output.textContent = result;
  detail.textContent = `${operation === 'encrypt' ? 'Encrypted' : 'Decrypted'} ${working.length} letters in ${working.length / 2} column-vector blocks using ${operation === 'encrypt' ? `[${matrix.join(', ')}]` : 'the modular inverse key'}.` + (working !== raw ? ' Added X padding for the odd-length message.' : '');
}
function updateKeyStatus() { keyStatus.textContent = validateKey(key()); }
inputs.forEach((input) => input.addEventListener('input', updateKeyStatus));
document.querySelector('#encrypt-button').addEventListener('click', () => transform('encrypt'));
document.querySelector('#decrypt-button').addEventListener('click', () => transform('decrypt'));
document.querySelector('#example-button').addEventListener('click', () => { message.value = 'HELP'; [3, 3, 2, 5].forEach((value, index) => { inputs[index].value = value; }); updateKeyStatus(); transform('encrypt'); });
updateKeyStatus();
