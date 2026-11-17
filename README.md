# MatrixCrypt Lab

A complete local mathematics laboratory for the classical 2×2 Hill cipher. React,
Vite, and TypeScript provide six responsive pages; FastAPI delegates every cipher
calculation to the original exact-integer Python engine.

**The Hill cipher is an educational historical cipher, unsuitable for real secrets.**
Successful round trips demonstrate implementation consistency, not security.

## The six workspaces

- **Command Center:** “Mathematics of Secrecy.” and a live, API-calculated HI → TC transformation.
- **Cipher Studio:** encryption/decryption, editable integer keys, determinant feedback,
  normalization and padding disclosure, clipboard copy, and expandable block calculations.
- **Matrix Playground:** live input/key updates, block selection, five calculation steps,
  highlighted rows, and determinant/adjugate/modular-inverse explanations for decryption.
- **Break the Cipher:** known-plaintext key reconstruction, invertible-column search,
  multiplication evidence, and verification against every supplied pair.
- **Experiment Intelligence:** fixed-message or seeded random trials, padding-aware
  verification, A–Z frequency counts/charts, a trial ledger, and CSV export.
- **Research Observatory:** validated anonymous survey CSV import, per-field counts,
  missing values, descriptive findings, methodology, and clear/reset controls.

No database, authentication, external service, or Docker is needed. Fonts are
bundled locally through Fontsource; the application makes no external font requests.

## Prerequisites

- Python **3.11 or newer** (verified with Python 3.14.6).
- Node.js **22.12+ or 24+**, with npm (verified with Node 24.21.0 and npm 12.2.2).
- Internet access for the initial dependency installation only.

## Install

From this existing checkout:

```sh
cd "/Users/jayanthv/Desktop/Cryptography and Matrices/matrixcrypt-lab"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
cd frontend
npm ci
```

`requirements.txt` declares supported top-level dependency ranges;
`requirements-lock.txt` pins the tested Python environment. `package-lock.json`
pins frontend dependencies. Virtual environments, node_modules, caches, builds,
local configuration, and upload directories are ignored by Git.

## Run locally

Terminal 1 — API:

```sh
cd "/Users/jayanthv/Desktop/Cryptography and Matrices/matrixcrypt-lab"
source .venv/bin/activate
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend:

```sh
cd "/Users/jayanthv/Desktop/Cryptography and Matrices/matrixcrypt-lab/frontend"
npm run dev -- --port 5173 --strictPort
```

- Application: <http://127.0.0.1:5173>
- API health: <http://127.0.0.1:8000/api/health>
- Interactive API reference: <http://127.0.0.1:8000/docs>
- OpenAPI contract: <http://127.0.0.1:8000/openapi.json>

Vite proxies `/api` to `http://127.0.0.1:8000`, so there is no CORS configuration
or secret to manage. To use another local API port, set the shell environment:

```sh
API_PROXY_TARGET=http://127.0.0.1:8001 npm run dev -- --port 5173 --strictPort
```

The same variable works for `npm run preview`. It is read by Vite's server
configuration, not exposed in the client bundle. No `.env` file is required.
Both servers bind to loopback by default. This is a local teaching application;
public hosting and production server hardening are outside its scope.

## Verify and build

```sh
cd "/Users/jayanthv/Desktop/Cryptography and Matrices/matrixcrypt-lab"
source .venv/bin/activate
python -m pytest -q
cd frontend
npm run typecheck
npm run build
npm run format:check
```

With the API running, preview the built application:

```sh
npm run preview -- --port 4173 --strictPort
```

Open <http://127.0.0.1:4173>. The preview also proxies `/api` to the local API.
Do not open `dist/index.html` directly from the filesystem.

After changing API models, regenerate the committed frontend contracts while the
API is running:

```sh
npm run types:api
npm run format
npm run typecheck
```

The original **66 tests** passed at baseline. The expanded suite has **133 passing
Python tests**, covering the engine, API validation, Unicode, recovery, experiments,
and survey parsing. Type checking and the production build pass. The installed
Starlette TestClient emits an upstream deprecation warning for its httpx adapter;
it does not affect the checks. Browser verification and repeatable manual scenarios
are recorded in [`matrixcrypt-lab/VERIFICATION.md`](matrixcrypt-lab/VERIFICATION.md).

## Mathematical conventions

All messages use **column vectors**, A=0 through Z=25:

```text
C = K × P mod 26
P = K⁻¹ × C mod 26
K = [[3, 3], [2, 5]]
K⁻¹ = [[15, 17], [20, 9]]
```

For HI: `[7, 8]ᵀ → [45, 54]ᵀ → [19, 2]ᵀ → TC`.
Other tested examples are OK → UA, GO → IE, HELP → HIAT,
MATRIX → KYETPB, CRYPTO → FLNTVE, and CAT → GEWX (padded CATX).

Only original ASCII A–Z/a–z characters enter the matrix calculation. Case is
normalized, and all characters excluded from the calculation are disclosed. Unicode letters are not transliterated or
expanded: for example, ß is excluded from the cipher, not converted to SS. Empty normalized input
is rejected. Encryption appends X for odd lengths. Decryption rejects odd-length
normalized ciphertext and preserves every trailing X because it may be genuine.

Cipher Studio enables **Preserve spacing and punctuation** by default. In this
mode, calculated letters replace the original ASCII letter slots; spaces, repeated
spaces, tabs, line breaks, punctuation, digits, and non-ASCII characters remain
unchanged and **unencrypted**. Copy the complete formatted ciphertext and leave the
option enabled when decrypting. Its layout travels with the ciphertext, without
stored plaintext or hidden browser state. Letters still return uppercase.

For example, `Hello world!` decrypts to `HELLO WORLD!`. If padding is needed,
the extra encrypted letter is appended after the original layout: `cat!` encrypts
to `GEW!X` and decrypts to `CAT!X`. Padding X is never silently removed. Disabling
the option produces the original A–Z-only output. Word boundaries already removed
from older ciphertext cannot be recovered automatically.

The API keeps its existing default (formatting disabled). Send
`"preserve_formatting": true` to `/api/cipher` to enable it. `display_output` holds
the display/copy result; `ciphertext`, `plaintext`, and block calculations retain
their existing mathematical meanings. The API returns `preserve_formatting` so
clients can label excluded characters accurately. Playground and experiments
continue using normalized letter streams.

Keys must be exactly 2×2 integer matrices, with `gcd(det K, 26) = 1`. Booleans,
strings, floats (including JSON `3.0`), and fractions are rejected. API entries
are bounded to ±1,000,000 and reduced modulo 26 for arithmetic. The determinant
in key validation refers to the supplied matrix; inverse calculations use its
reduced representative. No floating-point inversion is used.

### Known-plaintext recovery

Aligned two-letter blocks become **columns** of P and C; the engine computes
`K = C × P⁻¹ mod 26`. HI → TC and LP → AT recover the default key. With 2–30 pairs,
the engine searches pairs of columns for an invertible P and verifies the resulting
key against all evidence. An invertible P uniquely determines a linear matrix.
Contradictions therefore establish that no single Hill matrix matches all pairs;
a singular recovered matrix cannot be a valid invertible cipher key.

If no invertible pair of columns exists, this particular method cannot determine
a key. That does **not** prove that no key exists, nor does it exhaust more general
linear-congruence recovery methods.

### Experiments

Run 1–100 trials. Generated mode draws independent uniform A–Z characters with a
local Python `random.Random(seed)` instance (seed 0–2,147,483,647; length 1–200).
Equal settings reproduce results on the same Python runtime. This PRNG is for
reproducible experiments, not cryptographic use. Fixed mode repeats the same
supplied plaintext and key; its seed is unused. The key stays constant across
trials in both modes.

Verification compares decrypted output with **normalized, padded plaintext**.
Frequency charts aggregate padded plaintext (including X) and ciphertext across
all completed trials. CSV includes raw/normalized/padded plaintext, key, ciphertext,
recovered text, verification, mode, and seed. Cells resembling spreadsheet formulas
are escaped on export; the in-app plaintext remains unchanged.

## API overview

JSON request and response schemas are in `backend/api/models.py`, exposed in
OpenAPI and generated into `frontend/src/api-schema.d.ts`. Calculation modules
have no HTTP dependencies.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Local health check |
| `POST /api/key/validate` | `{ "key": [[3,3],[2,5]] }`; determinant/invertibility report |
| `POST /api/cipher` | `{ "text": "HI", "operation": "encrypt", "key": [[3,3],[2,5]] }`; computed explanation |
| `POST /api/recover` | `{ "pairs": [{"plaintext":"HI","ciphertext":"TC"},{"plaintext":"LP","ciphertext":"AT"}] }` |
| `POST /api/experiments` | `{ "mode":"generated", "count":10, "seed":42, "length":7, "key":[[3,3],[2,5]] }` |
| `POST /api/survey` | `{ "csv": "awareness\\nhigh\\n" }` (CSV string with actual newlines) |
| `GET /api/survey/template` | Download a headers-only CSV template |

Cipher plaintext is bounded to 2,000 characters; ciphertext accepts up to 2,001
to allow the complete formatted output plus padding. Fixed experiment plaintext
is bounded to 200 characters.
The transport rejects bodies above 1.1 MB before JSON parsing. Validation errors
use HTTP 422; excessive bodies use HTTP 413. Error bodies consistently have:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Check the highlighted input constraints.",
    "details": [{ "field": "key.0.0", "message": "Input should be a valid integer" }]
  }
}
```

Calculation errors provide an actionable message and an empty details list.
Recovery error codes distinguish `method_undetermined`, `inconsistent_evidence`,
and `invalid_recovered_key`. The UI clears stale results when inputs change and
ignores responses from superseded requests.

## Survey CSV schema and privacy

Use comma-delimited **UTF-8** CSV, optionally with a UTF-8 BOM. Maximum file size
is **1 MiB (1,048,576 bytes)** and maximum non-empty response count is **1,000**.
The downloadable template has headers only; no demonstration responses are loaded.
Include any non-empty subset of these exact column names:

| Column | Accepted values |
| --- | --- |
| `awareness` | `low`, `moderate`, `high` |
| `encryption_familiarity` | `none`, `basic`, `confident` |
| `two_factor` | `yes`, `no`, `unsure` |
| `password_practice` | `unique`, `reused`, `mixed` |
| `data_protection` | `low`, `moderate`, `high` |

Values are case insensitive; surrounding whitespace is trimmed. Blank cells are
missing, not negative answers. Entirely blank rows are skipped. Percentages use
the number answering **that field**, rounded to one decimal place; an entirely
missing field produces no finding. At least one non-empty response is required.
Unknown/duplicate headers, wrong cell counts, malformed CSV, null bytes, unsupported
values, invalid encoding, excessive size, and excessive row counts reject the file.
Errors identify the line/field where possible. `unique` means distinct passwords
across accounts, `reused` means repeated passwords, and `mixed` means a combination.

No names, emails, IDs, timestamps, or other identifying data are required or
accepted as columns. The browser sends the CSV to **your local Python process**,
which parses it in memory and returns only aggregate counts. The application
never writes raw uploads to disk, logs request bodies, or uses localStorage for
survey data. Clear, reload, or leave the page to discard its in-memory report.
Only user-requested CSV downloads are written by the browser.

Findings are descriptive. Convenience sampling, self-reporting, missing data,
small sample sizes, and selection bias prevent treating the results as population
estimates or evidence of causation. Collection dates and demographics are not inferred.

## Layout

```text
matrixcrypt-lab/
  backend/core/          # Existing engine plus recovery, experiments, survey analysis
  backend/api/           # FastAPI routes, request limits, typed contracts, errors
  tests/                 # Original engine tests and application regression tests
  frontend/src/          # Six pages, shared UI, generated API types, design tokens
  requirements.txt       # Direct dependency ranges
  requirements-lock.txt  # Tested Python environment
  VERIFICATION.md        # Browser checks and reproducible acceptance scenarios
```

## Remaining scope and verification limits

All six requested pages are implemented; there are no placeholder controls or
known unfinished features. Persistence, arbitrary matrix sizes, general congruence
solvers, public deployment, and inferential survey statistics are intentionally
outside this version. Browser checks used the Codex in-app browser on macOS;
Firefox, standalone Safari, and physical mobile devices were not separately tested.
