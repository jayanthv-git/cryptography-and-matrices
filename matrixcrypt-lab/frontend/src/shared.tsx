import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  AlertCircle,
  ArrowUpRight,
  Check,
  Copy,
  LoaderCircle,
} from "lucide-react";
import { api, type Block, type InverseSteps, type KeyReport } from "./api";

export const DEFAULT_KEY = ["3", "3", "2", "5"];
export function readKey(values: string[]) {
  if (values.some((v) => !/^-?\d+$/.test(v) || Math.abs(Number(v)) > 1_000_000))
    throw new Error(
      "Enter four whole numbers between −1,000,000 and 1,000,000. Empty, decimal, and fractional entries are not accepted.",
    );
  return [
    [Number(values[0]), Number(values[1])],
    [Number(values[2]), Number(values[3])],
  ];
}
export function useTask<T>() {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const version = useRef(0);
  const clear = useCallback(() => {
    version.current++;
    setData(null);
    setError("");
    setLoading(false);
  }, []);
  const run = useCallback(async (work: () => Promise<T>) => {
    const current = ++version.current;
    setData(null);
    setError("");
    setLoading(true);
    try {
      const result = await work();
      if (current === version.current) setData(result);
    } catch (e) {
      if (current === version.current)
        setError(
          e instanceof Error ? e.message : "The request failed. Please retry.",
        );
    } finally {
      if (current === version.current) setLoading(false);
    }
  }, []);
  useEffect(
    () => () => {
      version.current++;
    },
    [],
  );
  return { data, error, loading, run, clear };
}
export function PageHeader({
  section,
  title,
  children,
}: {
  section: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <header className="page-header">
      <div className="eyebrow">
        MATRIXCRYPT LAB <span>/</span> {section}
      </div>
      <h1>{title}</h1>
      <p>{children}</p>
    </header>
  );
}
export function Matrix({
  values,
  label,
  row,
  highlightAll = false,
}: {
  values: number[][];
  label?: string;
  row?: number;
  highlightAll?: boolean;
}) {
  return (
    <span className="matrix-wrap">
      {label && <span className="matrix-label">{label}</span>}
      <span
        className="matrix"
        role="img"
        aria-label={`${label || "Matrix"}: ${values.map((r) => r.join(", ")).join("; ")}`}
        style={{
          gridTemplateColumns: `repeat(${values[0]?.length || 2}, minmax(1.6em, auto))`,
        }}
      >
        {values.flatMap((r, i) =>
          r.map((v, j) => (
            <span
              key={`${i}-${j}`}
              className={row === i || highlightAll ? "selected-value" : ""}
            >
              {v}
            </span>
          )),
        )}
      </span>
    </span>
  );
}
export function KeyEditor({
  values,
  onChange,
}: {
  values: string[];
  onChange: (v: string[]) => void;
}) {
  const report = useTask<KeyReport>();
  useEffect(() => {
    report.clear();
    const timeout = setTimeout(() => {
      void report.run(() => api.key({ key: readKey(values) }));
    }, 180);
    return () => clearTimeout(timeout);
  }, [values, report.clear, report.run]);
  return (
    <fieldset className="key-field">
      <legend>
        Key matrix <span className="mono">K</span>
      </legend>
      <div className="key-line">
        <div className="matrix key-inputs">
          {values.map((value, i) => (
            <input
              key={i}
              aria-label={`Key row ${Math.floor(i / 2) + 1} column ${(i % 2) + 1}`}
              inputMode="numeric"
              value={value}
              onChange={(e) =>
                onChange(values.map((v, j) => (i === j ? e.target.value : v)))
              }
            />
          ))}
        </div>
        <div className="key-feedback" aria-live="polite">
          {report.loading ? (
            "Checking key…"
          ) : report.error ? (
            <span className="error-text">{report.error}</span>
          ) : report.data ? (
            <>
              <strong
                className={report.data.valid ? "valid-text" : "error-text"}
              >
                {report.data.valid ? "Invertible modulo 26" : "Not invertible"}
              </strong>
              <span className="mono">
                det K = {report.data.determinant}
                <br />
                gcd({report.data.determinant_mod26}, 26) = {report.data.gcd}
              </span>
            </>
          ) : (
            "Enter integer coefficients."
          )}
        </div>
      </div>
      <small>
        Entries reduce modulo 26. The determinant must be coprime to 26.
      </small>
    </fieldset>
  );
}
export function ErrorNotice({ error }: { error: string }) {
  return error ? (
    <div className="error-notice" role="alert">
      <AlertCircle size={18} />
      <span>{error}</span>
    </div>
  ) : null;
}
export function Loading() {
  return (
    <div className="loading" role="status">
      <LoaderCircle size={18} /> Calculating with the Python engine…
    </div>
  );
}
export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="empty-state">
      <span className="empty-symbol">[ · ]</span>
      <p>{children}</p>
    </div>
  );
}
export function ModeSwitch({
  mode,
  setMode,
}: {
  mode: "encrypt" | "decrypt";
  setMode: (m: "encrypt" | "decrypt") => void;
}) {
  return (
    <div className="segmented" aria-label="Operation">
      {(["encrypt", "decrypt"] as const).map((m) => (
        <button
          key={m}
          type="button"
          aria-pressed={mode === m}
          onClick={() => setMode(m)}
        >
          {m === "encrypt" ? "Encrypt" : "Decrypt"}
        </button>
      ))}
    </div>
  );
}
export function CopyButton({ value }: { value: string }) {
  const [state, setState] = useState("Copy output");
  useEffect(() => setState("Copy output"), [value]);
  return (
    <button
      className="button subtle"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          setState("Copied");
        } catch {
          setState("Copy unavailable — select the output");
        }
      }}
    >
      {state === "Copied" ? <Check size={16} /> : <Copy size={16} />}
      <span aria-live="polite">{state}</span>
    </button>
  );
}
export function RowCalculation({ block, row }: { block: Block; row?: number }) {
  return (
    <div className="row-calculations">
      {block.rows.map((r, i) => (
        <div key={i} className={row === i ? "active-row" : ""}>
          <span className="row-label">ROW {i + 1}</span>
          <div className="mono">
            <span>
              {r.terms
                .map((t) => `${t.coefficient} × ${t.value} (${t.product})`)
                .join(" + ")}
            </span>
            <span>
              = {r.sum} ≡ <b>{r.residue}</b> (mod {r.modulus}) →{" "}
              <b>{r.letter}</b>
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
export function InverseDetail({ steps }: { steps: InverseSteps }) {
  return (
    <section className="inverse-detail">
      <h3>From key to inverse</h3>
      <p className="mono">
        det K = {steps.determinant_expression} = {steps.determinant} ≡{" "}
        {steps.determinant_mod26} (mod 26)
      </p>
      <p className="mono">
        {steps.determinant_mod26}⁻¹ ≡ {steps.inverse_of_determinant};{" "}
        {steps.inverse_check.product} ≡ {steps.inverse_check.residue} (mod 26)
      </p>
      <div className="equation small-equation">
        <span>{steps.inverse_of_determinant} ×</span>
        <Matrix values={steps.adjugate} label="adj(K)" />
        <span>=</span>
        <Matrix values={steps.scaled_before_modulo} label="Before modulo" />
        <span>≡</span>
        <Matrix values={steps.inverse} label="K⁻¹" />
      </div>
      <p>{steps.explanation}</p>
    </section>
  );
}
export function DownloadLink({
  href,
  children,
}: {
  href: string;
  children: ReactNode;
}) {
  return (
    <a className="button secondary" href={href} download>
      {children}
      <ArrowUpRight size={16} />
    </a>
  );
}
export function downloadCSV(
  name: string,
  rows: (string | number | boolean)[][],
) {
  // Neutralize spreadsheet formulas in user-supplied plaintext cells.
  const csv = rows
    .map((row) =>
      row
        .map((v) => {
          const raw = String(v);
          const safe = /^[\s]*[=+@-]/.test(raw) ? `'${raw}` : raw;
          return `"${safe.replaceAll('"', '""')}"`;
        })
        .join(","),
    )
    .join("\r\n");
  const url = URL.createObjectURL(
    new Blob([csv], { type: "text/csv;charset=utf-8" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function FrequencyChart({
  title,
  values,
}: {
  title: string;
  values: Record<string, number>;
}) {
  const max = Math.max(1, ...Object.values(values));
  return (
    <figure className="frequency">
      <figcaption>
        {title}
        <span>{Object.values(values).reduce((a, b) => a + b, 0)} letters</span>
      </figcaption>
      <div
        className="bars"
        role="img"
        aria-label={`${title}. Counts available in the frequency table.`}
      >
        {Object.entries(values).map(([letter, count]) => (
          <div
            className="bar-column"
            key={letter}
            title={`${letter}: ${count}`}
          >
            <div className="bar-space">
              <span style={{ height: `${(count / max) * 100}%` }} />
            </div>
            <span>{letter}</span>
          </div>
        ))}
      </div>
      <details>
        <summary>View frequency counts</summary>
        <div className="frequency-counts">
          {Object.entries(values).map(([l, c]) => (
            <span key={l}>
              {l}: <b>{c}</b>
            </span>
          ))}
        </div>
      </details>
    </figure>
  );
}
