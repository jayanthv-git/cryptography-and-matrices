# Verification record

Verified locally on 17 November 2026. All survey responses used in browser QA were
synthetic test fixtures, not collected research data. No uploaded fixtures are
committed or bundled with the application.

## Automated checks

- Baseline: all 66 original Python tests passed before application integration.
- Expanded Python suite: 117 tests passed, including strict matrix/HTTP validation,
  all specified examples, Unicode expansion/surrogates, key-recovery success and
  failure classifications, seed reproducibility, padding-aware accounting, CSV
  encoding/shape/categories/missing values/limits, and request body limits.
- TypeScript strict type check passed.
- Vite production build passed; built preview served real API-backed MATRIX → KYETPB.
- Keyboard form submission and mobile-menu navigation passed. A 2,000-character
  input produced 2,000 output characters without page overflow at 320px.
- No browser console errors were observed in the final production session.
- Frontend source formatting check passed.
- npm dependency audit reported no vulnerabilities at installation.
- One upstream Starlette TestClient/httpx deprecation warning remains; no test failures.

## Browser acceptance checks

These were exercised through the actual UI against the running Python API. They
are repeatable manual acceptance scenarios, not a committed headless test suite.

| Page | Interaction and observed result |
| --- | --- |
| Command Center | Live default calculation HI → TC; vector [7,8], products 45/54, residues 19/2. Feature links and navigation open the appropriate pages. |
| Cipher Studio | HELP → HIAT. `cat! ß😀` → GEWX, normalized CAT, removed `! ß😀`, padding X. Expanded block details show actual arithmetic. |
| Cipher Studio | Copy produces GEWX in browser clipboard. Decryption returns CATX. A fractional key is rejected. Reset restores HELP/default key and clears output. |
| Playground | HI shows [7,8], [45,54], [19,2], TC. Row 2 changes highlighting. HELP updates blocks; choosing LP shows products 78/97 and AT. Next/Back change stages. |
| Playground | Changing the first coefficient to 5 updates HE → VI. Decrypt mode with that key shows determinant 19, modular inverse 11, adjugate, and inverse [[3,19],[4,3]]. |
| Recovery | HI → TC plus LP → AT recovers [[3,3],[2,5]], P determinant 17, and verifies both pairs. Add GO → AA produces inconsistent-evidence error. Remove/add controls work. |
| Recovery | AA → AA plus BB → FF produces an explicit method-undetermined explanation, not a fabricated key or claim that no key exists. |
| Experiments | Ten seed-42, seven-letter trials produce 10 successes/0 failures and 80 letters in each chart. Repeating yields identical rows. Export downloads the actual CSV ledger. |
| Experiments | Fixed CAT, three trials yields GEWX/CATX each time. Padded plaintext frequencies A/C/T/X each equal 3; counts accessible through chart disclosures. |
| Research | Empty before upload. Headers-only template downloads. Synthetic three-row/five-field CSV yields 3 responses; awareness 2 answered/1 missing and 50% low/50% high; 2FA 66.7% yes. |
| Research | Clear returns to empty. Invalid category identifies line 2/awareness. Invalid UTF-8 and >1 MiB files show actionable errors. |

## Responsive and accessibility checks

All six pages were inspected at desktop (1440px), tablet (768px), and mobile
(390px). Layout-width checks also passed at 320px. No page-level horizontal
overflow was observed; long ledgers scroll inside their table container. Mobile
navigation opens/closes and routes correctly. A headline overflow found during
QA was corrected. Route focus now uses preventScroll to avoid unwanted jumps.

Forms have accessible labels, toggles expose pressed state, steps expose the
current step, errors use alerts, and results/loading expose live status. Matrices
have textual labels. Charts expose counts; survey bars include readable values
and denominators. Buttons, disclosures, and forms use native keyboard interaction;
focus styling and reduced-motion CSS are included.

Browser checks were performed with the Codex in-app browser on macOS. These do
not substitute for cross-browser or screen-reader certification; Firefox,
standalone Safari, and physical mobile devices were not separately tested.

## Spacing preservation follow-up

- The expanded suite now has **133 passing tests**. New cases cover formatted
  ciphertext copied into a separate request; repeated spaces, tabs, newlines,
  punctuation, digits, and Unicode; genuine/trailing padding X; opt-out and old
  ciphertext; strict boolean validation; and the 2,000-character input boundary
  whose padded formatted output requires 2,001 ciphertext characters.
- Browser: `Hello  world!\nHI` encrypted to `HIOZE  IPJQL!\nTC`; Copy preserved
  both spaces and the newline. After a full page reload, decrypting that copied
  ciphertext returned `HELLO  WORLD!\nHI` with no original-message metadata.
- Disabling formatting cleared the prior result and yielded `HELLOWORLDHI`.
  Re-enabling restored the supplied ciphertext layout. The output preserves
  whitespace visually and labels retained non-A–Z characters as unencrypted.
- TypeScript/production build and formatting checks passed. Existing user-started
  frontend/backend processes were reused and left running.

## Explicit padding removal follow-up

- **149 Python tests pass**. New regression cases cover one-X removal, spaces and
  trailing newlines, punctuation/Unicode suffixes, original words ending in X,
  unchanged complete calculation blocks, strict request validation, and rejection
  when the decrypted message has no final X.
- Browser: the user's formatted screenshot ciphertext decrypted to the original
  sentence plus two newlines and X by default. With **Remove one padding X**
  selected, display and clipboard contained that sentence and the two newlines
  only; the calculation still ended in the correct BX block.
- Entering new ciphertext reset the removal choice. Selecting removal for TC
  (which decrypts to HI) showed an actionable error instead of deleting a letter.
- The option defaults off and clearly states that it assumes known padding.
  TypeScript/production build and formatting checks passed.
