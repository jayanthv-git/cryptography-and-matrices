import { useEffect } from "react";
import { ArrowDownRight, ArrowRight } from "lucide-react";
import { api, type CipherResult } from "./api";
import { ErrorNotice, Loading, Matrix, useTask } from "./shared";
export function Home() {
  const task = useTask<CipherResult>();
  useEffect(() => {
    void task.run(() =>
      api.cipher({
        text: "HI",
        operation: "encrypt",
        preserve_formatting: false,
      }),
    );
  }, [task.run]);
  const b = task.data?.blocks[0];
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">AN EXPLORATION IN LINEAR ALGEBRA</div>
          <h1>
            Mathematics
            <br />
            of <em>Secrecy.</em>
          </h1>
          <p>
            A message becomes a vector. A matrix becomes a key. Discover the
            elegant arithmetic—and revealing limitations—of the classical Hill
            cipher.
          </p>
          <div className="hero-actions">
            <a className="button champagne" href="#/cipher">
              Enter Cipher Studio
              <ArrowRight size={18} />
            </a>
            <a className="text-link" href="#/playground">
              Explore the mathematics
              <ArrowDownRight size={18} />
            </a>
          </div>
          <span className="hero-footnote">
            EXACT ARITHMETIC. EVERY STEP VISIBLE.
          </span>
        </div>
        <div className="hero-visual">
          <div className="section-heading">
            <span className="eyebrow">A MESSAGE, TRANSFORMED</span>
            <span className="tiny-label">01 → 02</span>
          </div>
          <ErrorNotice error={task.error} />
          {task.loading && <Loading />}
          {b && (
            <>
              <div className="transformation">
                <div>
                  <span>PLAINTEXT</span>
                  <strong>{b.source_block}</strong>
                  <small>A = 0, …, Z = 25</small>
                </div>
                <ArrowRight className="transform-arrow" />
                <div>
                  <span>CIPHERTEXT</span>
                  <strong>{b.result_block}</strong>
                  <small>modulo 26</small>
                </div>
              </div>
              <div className="hero-equation equation">
                <Matrix values={b.matrix} label="KEY" />
                <span>×</span>
                <Matrix
                  values={b.source_vector.map((v) => [v])}
                  label="INPUT"
                />
                <span>≡</span>
                <Matrix
                  values={b.result_vector.map((v) => [v])}
                  label="OUTPUT"
                />
              </div>
              <div className="hero-calculations">
                {b.rows.map((r, i) => (
                  <p key={i}>
                    {r.terms
                      .map((t) => `${t.coefficient} × ${t.value}`)
                      .join(" + ")}{" "}
                    = {r.sum} ≡ <b>{r.residue}</b> (mod 26)
                  </p>
                ))}
              </div>
              <div className="formula-note">
                <span>C = K × P mod 26</span>
                <span>Column-vector convention</span>
              </div>
            </>
          )}
        </div>
      </section>
      <section className="home-introduction">
        <span className="eyebrow">THE LABORATORY</span>
        <div>
          <h2>
            Understand the mechanism.
            <br />
            Then question its strength.
          </h2>
          <p>
            Move from individual calculations to reconstructing a secret key.
            Test the implementation, then explore how people understand the
            security around them.
          </p>
        </div>
      </section>
      <div className="feature-links">
        {[
          {
            n: "01",
            title: "Follow every calculation",
            text: "Encode, construct, multiply, reduce, and decode on an interactive mathematical canvas.",
            to: "playground",
            tag: "MATRIX PLAYGROUND",
          },
          {
            n: "02",
            title: "Recover the hidden key",
            text: "Use known plaintext and matrix inversion to reconstruct a key from real evidence.",
            to: "recover",
            tag: "BREAK THE CIPHER",
          },
          {
            n: "03",
            title: "Put the engine to the test",
            text: "Run seeded trials, inspect letter frequencies, and export verified round trips.",
            to: "experiments",
            tag: "EXPERIMENT INTELLIGENCE",
          },
          {
            n: "04",
            title: "Look beyond the algorithm",
            text: "Import anonymous survey responses and examine cybersecurity awareness.",
            to: "research",
            tag: "RESEARCH OBSERVATORY",
          },
        ].map((f) => (
          <a href={`#/${f.to}`} key={f.n}>
            <span className="feature-number">{f.n}</span>
            <div>
              <span className="eyebrow">{f.tag}</span>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
            <ArrowRight size={20} />
          </a>
        ))}
      </div>
      <div className="educational-note">
        <span className="mono">
          A HISTORICAL CIPHER.
          <br />A MODERN LEARNING TOOL.
        </span>
        <p>
          The Hill cipher exposes the beauty of modular linear algebra. Its
          linear structure also makes it vulnerable to known-plaintext attacks.
          It is unsuitable for protecting real secrets.
        </p>
      </div>
    </div>
  );
}
