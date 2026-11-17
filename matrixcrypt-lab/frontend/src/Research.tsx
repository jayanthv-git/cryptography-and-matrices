import { useRef, useState } from "react";
import { FileUp, RotateCcw } from "lucide-react";
import { api, type SurveyResult } from "./api";
import {
  DownloadLink,
  ErrorNotice,
  Loading,
  PageHeader,
  useTask,
} from "./shared";
const FIELDS = [
  ["awareness", "Cybersecurity awareness", "low, moderate, high"],
  [
    "encryption_familiarity",
    "Encryption familiarity",
    "none, basic, confident",
  ],
  ["two_factor", "Two-factor authentication", "yes, no, unsure"],
  ["password_practice", "Password practices", "unique, reused, mixed"],
  ["data_protection", "Data-protection understanding", "low, moderate, high"],
];
export function Research() {
  const task = useTask<SurveyResult>();
  const fileInput = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");
  const r = task.data;
  async function importFile(file: File) {
    setFileName(file.name);
    await task.run(async () => {
      if (file.size > 1_048_576)
        throw new Error(
          "File exceeds 1 MiB. Export a smaller CSV (at most 1,000 response rows).",
        );
      let content: string;
      try {
        content = new TextDecoder("utf-8", { fatal: true }).decode(
          await file.arrayBuffer(),
        );
      } catch {
        throw new Error(
          "File is not valid UTF-8. Export it again as UTF-8 CSV.",
        );
      }
      return api.survey({ csv: content });
    });
  }
  return (
    <>
      <PageHeader
        section="05 / RESEARCH OBSERVATORY"
        title="From responses to understanding."
      >
        Examine cybersecurity awareness through your own survey data.
        Transparent counts, explicit denominators, and no invented findings.
      </PageHeader>
      <section className="research-intro">
        <div>
          <span className="eyebrow">YOUR DATA, IN CONTEXT</span>
          <h2>{r ? "An imported snapshot." : "Start with real responses."}</h2>
          <p>
            Import an anonymous CSV to explore awareness, familiarity, and
            reported habits. Include only the template’s fields; identifying
            information is neither needed nor accepted.
          </p>
          <p className="note">
            CSV contents are sent to your locally running Python API and
            processed in memory. The application does not save raw uploads,
            responses, or reports to disk or browser storage. Reloading or
            clearing removes the displayed report.
          </p>
        </div>
        <div className="upload-area">
          <FileUp size={30} />
          <h3>Import survey responses</h3>
          <p>UTF-8 CSV · up to 1 MiB · 1,000 rows</p>
          <input
            className="file-input"
            aria-label="Upload survey CSV"
            ref={fileInput}
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void importFile(file);
            }}
          />
          <DownloadLink href="/api/survey/template">
            Download CSV template
          </DownloadLink>
          {fileName && <span className="file-name">{fileName}</span>}
        </div>
      </section>
      <ErrorNotice error={task.error} />
      {task.loading && <Loading />}
      <details className="schema-panel">
        <summary>Accepted CSV schema & missing values</summary>
        <p>
          Include any subset of the columns below, with exact lowercase headers
          and at least one response. Values are case insensitive; surrounding
          whitespace is ignored. Blank cells are missing, not negative answers.
          Entirely blank rows are skipped. Unknown or duplicate headers and
          invalid category values reject the import.
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Column</th>
                <th>Accepted values</th>
              </tr>
            </thead>
            <tbody>
              {FIELDS.map(([key, , values]) => (
                <tr key={key}>
                  <td>{key}</td>
                  <td>{values}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">
          The template contains headers only. “unique” means unique passwords
          across accounts; “reused” means repeated passwords; “mixed” means a
          mix. Define these response choices consistently when collecting data.
        </p>
      </details>
      {r ? (
        <section className="survey-report">
          <div className="section-heading">
            <h2>Response report</h2>
            <button
              className="button subtle"
              onClick={() => {
                task.clear();
                setFileName("");
                if (fileInput.current) fileInput.current.value = "";
              }}
            >
              <RotateCcw size={16} />
              Clear data
            </button>
          </div>
          <div className="report-summary">
            <strong>{r.responses}</strong>
            <div>
              <b>imported responses</b>
              <span>
                {r.fields.length} fields included · {r.skipped_empty_rows} empty
                rows skipped
              </span>
            </div>
          </div>
          <div className="survey-fields">
            {r.fields.map((field) => (
              <section key={field.name} className="survey-field">
                <h3>{FIELDS.find((f) => f[0] === field.name)?.[1]}</h3>
                <p className="note">
                  {field.answered} answered · {field.missing} missing ·
                  percentages of answered responses
                </p>
                <div className="survey-bars">
                  {field.categories.map((category) => (
                    <div className="survey-bar" key={category.label}>
                      <span>{category.label}</span>
                      <div className="survey-track">
                        <span style={{ width: `${category.percentage}%` }} />
                      </div>
                      <span>
                        {category.count} <small>({category.percentage}%)</small>
                      </span>
                    </div>
                  ))}
                </div>
                <p className="finding">
                  {field.answered
                    ? field.categories
                        .filter((c) => c.count > 0)
                        .map(
                          (c) =>
                            `${c.count} of ${field.answered} (${c.percentage}%) selected “${c.label}”`,
                        )
                        .join("; ") + "."
                    : "No answered values in this field; no finding can be calculated."}
                </p>
              </section>
            ))}
          </div>
        </section>
      ) : (
        !task.loading && (
          <div className="research-empty">
            <span className="mono">NO DATA IMPORTED</span>
            <p>There are no response counts or findings to report yet.</p>
          </div>
        )
      )}
      <section className="methodology">
        <span className="eyebrow">READ THE RESULTS RESPONSIBLY</span>
        <h2>Methodology & limitations</h2>
        <div>
          <p>
            <b>Descriptive analysis.</b> Counts summarize the file you import.
            Each field uses its own non-missing denominator. Percentages are
            rounded to one decimal place and may not total exactly 100%.
          </p>
          <p>
            <b>Sampling & sample size.</b> A convenience sample cannot represent
            a broader population by default. Small samples are unstable, and
            selection bias can remain even in large samples.
          </p>
          <p>
            <b>Self-reporting & missing data.</b> Answers reflect reported
            knowledge and habits, not verified behavior. Nonresponse may be
            systematic. No collection dates, identities, or causal conclusions
            are inferred.
          </p>
        </div>
      </section>
    </>
  );
}
