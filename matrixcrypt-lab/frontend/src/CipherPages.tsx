import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, RotateCcw } from "lucide-react";
import { api, type CipherResult, type Mode } from "./api";
import {
  CopyButton,
  DEFAULT_KEY,
  Empty,
  ErrorNotice,
  InverseDetail,
  KeyEditor,
  Loading,
  Matrix,
  ModeSwitch,
  PageHeader,
  readKey,
  RowCalculation,
  useTask,
} from "./shared";

export function CipherStudio() {
  const [mode, setMode] = useState<Mode>("encrypt");
  const [text, setText] = useState("HELP");
  const [key, setKey] = useState(DEFAULT_KEY);
  const task = useTask<CipherResult>();
  const change = (action: () => void) => {
    action();
    task.clear();
  };
  const result = task.data;
  const output = result
    ? result.operation === "encrypt"
      ? result.ciphertext
      : result.plaintext || ""
    : "";
  return (
    <>
      <PageHeader
        section="01 / CIPHER STUDIO"
        title="Letters in. Mathematics out."
      >
        Transform a message with a 2 × 2 key. Follow the exact arithmetic behind
        every pair of letters.
      </PageHeader>
      <div className="studio-grid">
        <form
          className="workspace input-workspace"
          onSubmit={(e) => {
            e.preventDefault();
            void task.run(() =>
              api.cipher({ text, key: readKey(key), operation: mode }),
            );
          }}
        >
          <div className="section-heading">
            <span className="eyebrow">THE INPUT</span>
            <ModeSwitch mode={mode} setMode={(m) => change(() => setMode(m))} />
          </div>
          <label className="field-label" htmlFor="cipher-text">
            {mode === "encrypt" ? "Plaintext" : "Ciphertext"}
          </label>
          <textarea
            id="cipher-text"
            value={text}
            maxLength={2000}
            onChange={(e) => change(() => setText(e.target.value))}
            placeholder="Enter a message…"
          />
          <div className="input-caption">
            <span>ASCII A–Z · case insensitive</span>
            <span>{text.length}/2,000</span>
          </div>
          <KeyEditor values={key} onChange={(v) => change(() => setKey(v))} />
          <div className="actions">
            <button
              className="button primary"
              disabled={task.loading}
              type="submit"
            >
              {task.loading
                ? "Calculating…"
                : mode === "encrypt"
                  ? "Encrypt message"
                  : "Decrypt message"}
              <ArrowRight size={17} />
            </button>
            <button
              type="button"
              className="button subtle"
              onClick={() => {
                setMode("encrypt");
                setText("HELP");
                setKey(DEFAULT_KEY);
                task.clear();
              }}
            >
              <RotateCcw size={16} />
              Reset
            </button>
          </div>
          <ErrorNotice error={task.error} />
          <p className="note">
            Only ASCII letters are retained. Encryption pads an odd-length
            message with X; decryption keeps trailing X.
          </p>
        </form>
        <section
          className={`output-workspace ${result ? "has-result" : ""}`}
          aria-live="polite"
        >
          <div className="section-heading">
            <span className="eyebrow">THE OUTPUT</span>
            <span className="tiny-label">MOD 26</span>
          </div>
          {task.loading ? (
            <Loading />
          ) : result ? (
            <>
              <span className="output-label">
                {result.operation === "encrypt"
                  ? "CIPHERTEXT"
                  : "RECOVERED PLAINTEXT"}
              </span>
              <div className="cipher-output" data-testid="cipher-output">
                {output}
              </div>
              <CopyButton value={output} />
              <dl className="metadata">
                <div>
                  <dt>Normalized input</dt>
                  <dd>{result.normalized ?? result.normalized_ciphertext}</dd>
                </div>
                <div>
                  <dt>Removed characters</dt>
                  <dd>
                    {result.removed_characters
                      ? JSON.stringify(result.removed_characters)
                      : "None"}
                  </dd>
                </div>
                <div>
                  <dt>Padding</dt>
                  <dd>
                    {result.operation === "encrypt"
                      ? result.padding_count
                        ? `Added ${result.padding_added} → ${result.padded_plaintext}`
                        : "None needed"
                      : "Trailing X preserved"}
                  </dd>
                </div>
              </dl>
              <div className="active-key">
                <Matrix values={result.key} label="Active K" />
                {result.inverse_key && (
                  <Matrix values={result.inverse_key} label="K⁻¹" />
                )}
              </div>
            </>
          ) : (
            <Empty>
              Your calculated result will appear here.
              <br />
              Enter a message and execute the transformation.
            </Empty>
          )}
        </section>
      </div>
      {result && (
        <section className="calculation-section">
          <div className="section-heading">
            <h2>Inspect the calculation.</h2>
            <span className="tiny-label">
              {result.blocks.length} BLOCKS · COLUMN VECTORS
            </span>
          </div>
          {result.inverse_steps && (
            <InverseDetail steps={result.inverse_steps} />
          )}
          <div className="block-list">
            {result.blocks.map((b) => (
              <details key={b.index}>
                <summary>
                  <span className="block-index">
                    {String(b.index + 1).padStart(2, "0")}
                  </span>
                  <span className="mono">
                    {b.source_block} <span className="muted">→</span>{" "}
                    {b.result_block}
                  </span>
                  <span className="block-summary">
                    [{b.source_vector.join(", ")}] → [
                    {b.result_vector.join(", ")}]
                  </span>
                </summary>
                <RowCalculation block={b} />
              </details>
            ))}
          </div>
        </section>
      )}
    </>
  );
}

const STEPS = [
  "Encode",
  "Construct Vectors",
  "Multiply",
  "Apply Modulo",
  "Decode",
];
export function Playground() {
  const [mode, setMode] = useState<Mode>("encrypt");
  const [text, setText] = useState("HI");
  const [key, setKey] = useState(DEFAULT_KEY);
  const [blockIndex, setBlockIndex] = useState(0);
  const [step, setStep] = useState(0);
  const [row, setRow] = useState(0);
  const task = useTask<CipherResult>();
  useEffect(() => {
    task.clear();
    setBlockIndex(0);
    const timer = setTimeout(() => {
      void task.run(() =>
        api.cipher({ text, key: readKey(key), operation: mode }),
      );
    }, 250);
    return () => clearTimeout(timer);
  }, [text, key, mode, task.clear, task.run]);
  const result = task.data;
  const block = result?.blocks[blockIndex];
  return (
    <>
      <PageHeader
        section="02 / MATRIX PLAYGROUND"
        title="See the cipher think."
      >
        One block. Five steps. Change the message or key to watch each
        calculation update.
      </PageHeader>
      <div className="playground-controls workspace">
        <div>
          <ModeSwitch
            mode={mode}
            setMode={(m) => {
              task.clear();
              setMode(m);
              setText(m === "encrypt" ? "HI" : "TC");
            }}
          />
          <label className="field-label" htmlFor="play-message">
            {mode === "encrypt" ? "Message" : "Ciphertext"}
          </label>
          <input
            id="play-message"
            className="message-input"
            value={text}
            maxLength={2000}
            onChange={(e) => {
              task.clear();
              setText(e.target.value);
            }}
          />
          <small>Non-ASCII letters and other characters are removed.</small>
        </div>
        <KeyEditor
          values={key}
          onChange={(v) => {
            task.clear();
            setKey(v);
          }}
        />
      </div>
      <ErrorNotice error={task.error} />
      {task.loading && <Loading />}
      {result && block && (
        <>
          <div className="canvas-top">
            <label>
              Message block{" "}
              <select
                aria-label="Message block"
                value={blockIndex}
                onChange={(e) => setBlockIndex(Number(e.target.value))}
              >
                {result.blocks.map((b) => (
                  <option key={b.index} value={b.index}>
                    {b.index + 1} · {b.source_block} → {b.result_block}
                  </option>
                ))}
              </select>
            </label>
            <span className="tiny-label">
              {mode === "encrypt" ? "C = K × P" : "P = K⁻¹ × C"} (MOD 26)
            </span>
          </div>
          <nav className="stepper" aria-label="Calculation steps">
            {STEPS.map((name, i) => (
              <button
                key={name}
                className={step === i ? "current" : step > i ? "completed" : ""}
                aria-current={step === i ? "step" : undefined}
                onClick={() => setStep(i)}
              >
                <span>{String(i + 1).padStart(2, "0")}</span>
                {name}
              </button>
            ))}
          </nav>
          <section className="math-canvas" aria-live="polite">
            <div className="canvas-description">
              <span className="eyebrow">STEP {step + 1} / 5</span>
              <h2>
                {
                  [
                    "Every letter has a number.",
                    "Build a column vector.",
                    "Multiply, row by row.",
                    "Wrap around the alphabet.",
                    "Numbers become letters.",
                  ][step]
                }
              </h2>
              <p>
                {
                  [
                    "A maps to 0, B to 1, and so on through Z = 25.",
                    "Place the two letter values vertically, in their original order.",
                    "Take the dot product of each key row with the input column.",
                    "Reduce each integer sum to its remainder on division by 26.",
                    "Map each remainder back to A–Z, preserving row order.",
                  ][step]
                }
              </p>
            </div>
            {step === 0 && (
              <div className="letter-mapping">
                {block.source_letters.map((l, i) => (
                  <div key={i}>
                    <span>{l.letter}</span>
                    <ArrowRight />
                    <b>{l.number}</b>
                  </div>
                ))}
              </div>
            )}
            {step === 1 && (
              <div className="equation">
                <span className="big-letters">{block.source_block}</span>
                <ArrowRight />
                <Matrix
                  values={block.source_vector.map((v) => [v])}
                  label={mode === "encrypt" ? "P" : "C"}
                />
              </div>
            )}
            {step === 2 && (
              <>
                <div className="row-picker">
                  <span>Inspect a row</span>
                  {[0, 1].map((r) => (
                    <button
                      key={r}
                      aria-pressed={row === r}
                      onClick={() => setRow(r)}
                    >
                      Row {r + 1}
                    </button>
                  ))}
                </div>
                <div className="equation">
                  <Matrix
                    values={block.matrix}
                    label={mode === "encrypt" ? "K" : "K⁻¹"}
                    row={row}
                  />
                  <span>×</span>
                  <Matrix
                    values={block.source_vector.map((v) => [v])}
                    label="Input"
                    highlightAll
                  />
                  <span>=</span>
                  <Matrix
                    values={block.rows.map((r) => [r.sum])}
                    label="Products"
                    row={row}
                  />
                </div>
                <RowCalculation block={block} row={row} />
              </>
            )}
            {step === 3 && (
              <div className="equation">
                <Matrix
                  values={block.rows.map((r) => [r.sum])}
                  label="Products"
                />
                <span>mod 26 =</span>
                <Matrix
                  values={block.result_vector.map((v) => [v])}
                  label="Remainders"
                />
              </div>
            )}
            {step === 4 && (
              <div className="equation">
                <Matrix
                  values={block.result_vector.map((v) => [v])}
                  label="Remainders"
                />
                <ArrowRight />
                <span className="big-letters">{block.result_block}</span>
              </div>
            )}
            <div className="step-actions">
              <button
                className="button subtle"
                disabled={step === 0}
                onClick={() => setStep((s) => s - 1)}
              >
                <ArrowLeft size={16} />
                Back
              </button>
              <span className="mono">{step + 1} / 5</span>
              <button
                className="button primary"
                disabled={step === 4}
                onClick={() => setStep((s) => s + 1)}
              >
                Next
                <ArrowRight size={16} />
              </button>
            </div>
          </section>
          <p className="normalization-note">
            Normalized:{" "}
            <b>{result.normalized ?? result.normalized_ciphertext}</b> ·
            Removed:{" "}
            {result.removed_characters
              ? JSON.stringify(result.removed_characters)
              : "none"}{" "}
            ·{" "}
            {mode === "encrypt"
              ? `Padding: ${result.padding_added || "none"}`
              : "Trailing X preserved"}
          </p>
          {result.inverse_steps && (
            <InverseDetail steps={result.inverse_steps} />
          )}
        </>
      )}
      {!result && !task.loading && !task.error && (
        <Empty>Preparing the calculation…</Empty>
      )}
    </>
  );
}
