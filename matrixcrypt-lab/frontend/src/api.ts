import type { components } from "./api-schema";
type S = components["schemas"];
export type CipherResult = S["CipherResponse"];
export type KeyReport = S["KeyReport"];
export type RecoveryResult = S["RecoveryResponse"];
export type ExperimentResult = S["ExperimentResponse"];
export type SurveyResult = S["SurveyResponse"];
export type Block = S["Block"];
export type InverseSteps = S["InverseSteps"];
export type Mode = "encrypt" | "decrypt";
async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`/api/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      S["ErrorResponse"] | null;
    throw new Error(
      payload?.error
        ? [
            payload.error.message,
            ...(payload.error.details ?? []).map(
              (d) => `${d.field}: ${d.message}`,
            ),
          ].join(" ")
        : `API returned ${response.status}. Check that the backend is running.`,
    );
  }
  return response.json() as Promise<T>;
}
export const api = {
  cipher: (body: S["CipherRequest"]) => post<CipherResult>("cipher", body),
  key: (body: S["KeyRequest"]) => post<KeyReport>("key/validate", body),
  recover: (body: S["RecoveryRequest"]) =>
    post<RecoveryResult>("recover", body),
  experiments: (body: S["ExperimentRequest"]) =>
    post<ExperimentResult>("experiments", body),
  survey: (body: S["SurveyRequest"]) => post<SurveyResult>("survey", body),
};
