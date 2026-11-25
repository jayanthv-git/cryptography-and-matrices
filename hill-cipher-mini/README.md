# Hill Cipher Mini Lab

A tiny, dependency-free 2×2 Hill cipher playground. Open `index.html` in a browser, enter a message and an invertible key matrix, then encrypt or decrypt.

The tool uses A=0 through Z=25, column vectors, and arithmetic modulo 26. Odd-length plaintext receives an explicit trailing `X` during encryption. It is an educational demonstration of matrix arithmetic, not a secure encryption tool.

## Example

The default key is `[[3, 3], [2, 5]]`. Encrypting `HELP` produces `HIAT`.
