import { useState } from "react";
import { ArrowRight, Plus, Trash2, Check } from "lucide-react";
import { api, type RecoveryResult } from "./api";
import {
  Empty,
  ErrorNotice,
  Loading,
  Matrix,
  PageHeader,
  useTask,
} from "./shared";
export function Recovery() {
  const [pairs, setPairs] = useState([
    { plaintext: "HI", ciphertext: "TC" },
    { plaintext: "LP", ciphertext: "AT" },
  ]);
  const task = useTask<RecoveryResult>();
  function update(
    index: number,
    field: "plaintext" | "ciphertext",
    value: string,
  ) {
    task.clear();
    setPairs(pairs.map((p, i) => (i === index ? { ...p, [field]: value } : p)));
  }
  const r = task.data;
  return (
    <>
      <PageHeader
        section="03 / BREAK THE CIPHER"
        title="A little evidence. A complete key."
      >
        A known-plaintext attack reveals why linear algebra alone cannot keep a
        secret. Supply aligned letter pairs and reconstruct the key.
      </PageHeader>
      <div className="investigation">
        <section className="evidence-panel workspace">
          <div className="stage-label">
            <span>01</span>
            <h2>Evidence</h2>
          </div>
          <p>
            Each row pairs two known plaintext letters with their two ciphertext
            letters. Use exactly A–Z; no spaces.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void task.run(() => api.recover({ pairs }));
            }}
          >
            <div className="evidence-head">
              <span>PLAINTEXT</span>
              <span>CIPHERTEXT</span>
            </div>
            {pairs.map((pair, i) => (
              <div className="evidence-pair" key={i}>
                <label className="sr-only" htmlFor={`p-${i}`}>
                  Plaintext pair {i + 1}
                </label>
                <input
                  id={`p-${i}`}
                  value={pair.plaintext}
                  maxLength={2}
                  onChange={(e) => update(i, "plaintext", e.target.value)}
                />
                <ArrowRight size={16} />
                <label className="sr-only" htmlFor={`c-${i}`}>
                  Ciphertext pair {i + 1}
                </label>
                <input
                  id={`c-${i}`}
                  value={pair.ciphertext}
                  maxLength={2}
                  onChange={(e) => update(i, "ciphertext", e.target.value)}
                />
                <button
                  className="icon-button"
                  type="button"
                  aria-label={`Remove pair ${i + 1}`}
                  disabled={pairs.length <= 1}
                  onClick={() => {
                    task.clear();
                    setPairs(pairs.filter((_, j) => j !== i));
                  }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
            <button
              className="button subtle"
              type="button"
              disabled={pairs.length >= 30}
              onClick={() => {
                task.clear();
                setPairs([...pairs, { plaintext: "", ciphertext: "" }]);
              }}
            >
              <Plus size={16} />
              Add evidence pair
            </button>
            <div className="actions">
              <button className="button primary" disabled={task.loading}>
                Recover key
                <ArrowRight size={16} />
              </button>
            </div>
            <ErrorNotice error={task.error} />
          </form>
          <p className="note">
            Two usable columns are enough. With more evidence, we search all
            column pairs and verify the recovered key against every row.
          </p>
        </section>
        <div className="reconstruction">
          <section>
            <div className="stage-label">
              <span>02</span>
              <h2>Reconstruction</h2>
            </div>
            {task.loading ? (
              <Loading />
            ) : r ? (
              <>
                <p>
                  Using evidence pairs{" "}
                  {r.selected_pair_indices.map((i) => i + 1).join(" and ")} as
                  columns.
                </p>
                <div className="equation">
                  <Matrix values={r.plaintext_matrix} label="P" />
                  <Matrix values={r.ciphertext_matrix} label="C" />
                </div>
                <p className="mono">
                  det P = {r.determinant} ≡ {r.determinant_mod26} (mod 26)
                </p>
                <div className="equation small-equation">
                  <Matrix values={r.ciphertext_matrix} label="C" />
                  <span>×</span>
                  <Matrix values={r.plaintext_inverse} label="P⁻¹" />
                  <span>=</span>
                  <Matrix values={r.products} label="Products" />
                </div>
                <p className="note">
                  Reduce each product modulo 26 to obtain K.
                </p>
              </>
            ) : (
              <Empty>
                The plaintext columns must form an invertible matrix modulo 26
                before this method can recover a key.
              </Empty>
            )}
          </section>
          <section className={`discovery ${r ? "revealed" : ""}`}>
            <div className="stage-label">
              <span>03</span>
              <h2>Discovery</h2>
            </div>
            {r ? (
              <>
                <div className="discovery-key">
                  <span className="formula">K = C × P⁻¹ mod 26</span>
                  <Matrix values={r.key} label="Recovered key" />
                </div>
                <h3>All evidence verified</h3>
                <ul className="verification-list">
                  {r.verification.map((v, i) => (
                    <li key={i}>
                      <span className="mono">
                        {v.plaintext} → {v.predicted}
                      </span>
                      <span>
                        <Check size={14} /> Matches {v.ciphertext}
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p>
                A recovered key appears only after successful reconstruction and
                verification.
              </p>
            )}
          </section>
        </div>
      </div>
    </>
  );
}
