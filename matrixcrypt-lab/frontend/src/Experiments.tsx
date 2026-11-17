import { useState } from "react";
import { ArrowRight, Download } from "lucide-react";
import { api, type ExperimentResult } from "./api";
import {
  DEFAULT_KEY,
  downloadCSV,
  Empty,
  ErrorNotice,
  FrequencyChart,
  KeyEditor,
  Loading,
  PageHeader,
  readKey,
  useTask,
} from "./shared";
export function Experiments() {
  const [mode, setMode] = useState<"fixed" | "generated">("generated");
  const [plaintext, setPlaintext] = useState("MATRIX");
  const [count, setCount] = useState("10");
  const [seed, setSeed] = useState("42");
  const [length, setLength] = useState("7");
  const [key, setKey] = useState(DEFAULT_KEY);
  const task = useTask<ExperimentResult>();
  const change = (fn: () => void) => {
    fn();
    task.clear();
  };
  const r = task.data;
  function exportRows() {
    if (!r) return;
    downloadCSV("matrixcrypt-experiments.csv", [
      [
        "test_id",
        "plaintext",
        "normalized",
        "padded_plaintext",
        "key",
        "ciphertext",
        "recovered",
        "verified",
        "mode",
        "seed",
      ],
      ...r.rows.map((row) => [
        row.id,
        row.plaintext,
        row.normalized,
        row.padded_plaintext,
        JSON.stringify(row.key),
        row.ciphertext,
        row.recovered,
        row.verified,
        r.mode,
        r.seed,
      ]),
    ]);
  }
  return (
    <>
      <PageHeader
        section="04 / EXPERIMENT INTELLIGENCE"
        title="Test the transformation."
      >
        Run reproducible trials. Compare letter frequencies and check that each
        encrypted message returns to its normalized, padded plaintext.
      </PageHeader>
      <form
        className="experiment-form workspace"
        onSubmit={(e) => {
          e.preventDefault();
          void task.run(() =>
            api.experiments({
              mode,
              plaintext,
              count: Number(count),
              seed: Number(seed),
              length: Number(length),
              key: readKey(key),
            }),
          );
        }}
      >
        <div className="experiment-parameters">
          <label>
            Message source
            <select
              value={mode}
              onChange={(e) =>
                change(() => setMode(e.target.value as "fixed" | "generated"))
              }
            >
              <option value="generated">Seeded random A–Z messages</option>
              <option value="fixed">Repeat my plaintext</option>
            </select>
          </label>
          {mode === "fixed" ? (
            <label>
              Plaintext
              <input
                value={plaintext}
                maxLength={200}
                onChange={(e) => change(() => setPlaintext(e.target.value))}
              />
            </label>
          ) : (
            <label>
              Letters per message
              <input
                type="number"
                min="1"
                max="200"
                required
                value={length}
                onChange={(e) => change(() => setLength(e.target.value))}
              />
            </label>
          )}
          <div className="two-fields">
            <label>
              Trials (1–100)
              <input
                type="number"
                min="1"
                max="100"
                required
                value={count}
                onChange={(e) => change(() => setCount(e.target.value))}
              />
            </label>
            <label>
              Seed
              <input
                type="number"
                min="0"
                max="2147483647"
                required
                value={seed}
                disabled={mode === "fixed"}
                onChange={(e) => change(() => setSeed(e.target.value))}
              />
            </label>
          </div>
          <p className="note">
            {mode === "generated"
              ? "Each trial draws a new uniformly sampled A–Z message from Python’s seeded generator. The key stays fixed. Equal settings reproduce the same sequence."
              : "Every trial uses the same supplied message and key. This is a deterministic repeatability check; seed is unused."}
          </p>
        </div>
        <div>
          <KeyEditor values={key} onChange={(v) => change(() => setKey(v))} />
          <button className="button primary" disabled={task.loading}>
            {task.loading ? "Running…" : "Run experiment"}
            <ArrowRight size={16} />
          </button>
        </div>
      </form>
      <ErrorNotice error={task.error} />
      {task.loading && <Loading />}
      {r ? (
        <>
          <div className="experiment-summary" aria-live="polite">
            <div>
              <span>COMPLETED</span>
              <strong>{r.completed}</strong>
            </div>
            <div>
              <span>SUCCESSFUL</span>
              <strong>{r.successful}</strong>
            </div>
            <div>
              <span>FAILED</span>
              <strong>{r.failed}</strong>
            </div>
            <p>
              A successful round trip verifies implementation consistency. It
              does not establish cryptographic security.
            </p>
          </div>
          <div className="charts-grid">
            <FrequencyChart
              title="Padded plaintext · A–Z frequency"
              values={r.plaintext_frequency}
            />
            <FrequencyChart
              title="Ciphertext · A–Z frequency"
              values={r.ciphertext_frequency}
            />
          </div>
          <div className="section-heading">
            <h2>Trial ledger</h2>
            <button className="button secondary" onClick={exportRows}>
              <Download size={16} />
              Export CSV
            </button>
          </div>
          <p className="note">
            Frequencies count all padded plaintext and ciphertext letters across
            completed trials. Recovered text retains padding X.
          </p>
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Experiment results"
          >
            <table>
              <thead>
                <tr>
                  {[
                    "Test",
                    "Plaintext",
                    "Key",
                    "Ciphertext",
                    "Recovered",
                    "Verification",
                  ].map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {r.rows.map((row) => (
                  <tr key={row.id}>
                    <td>{String(row.id).padStart(3, "0")}</td>
                    <td title={`Padded: ${row.padded_plaintext}`}>
                      {row.plaintext}
                    </td>
                    <td className="nowrap">{JSON.stringify(row.key)}</td>
                    <td>{row.ciphertext}</td>
                    <td>{row.recovered}</td>
                    <td>
                      <span
                        className={row.verified ? "verified" : "error-text"}
                      >
                        {row.verified ? "Passed" : "Failed"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        !task.loading && (
          <Empty>
            Your experiment results, frequency distributions, and downloadable
            trial ledger will appear here.
          </Empty>
        )
      )}
    </>
  );
}
