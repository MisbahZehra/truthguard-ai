import type { AppConfig, HistoryItem, Verification } from "./types";
export class ApiError extends Error { constructor(public code: string, message: string, public requestId?: string) { super(message); } }
async function call<T>(path: string, init?: RequestInit, text = false): Promise<T> {
  let res: Response;
  try { res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...init }); }
  catch { throw new ApiError("network", "Cannot reach the TruthGuard server. Is the backend running?"); }
  if (!res.ok) {
    let e: any = {}; try { e = (await res.json()).error ?? {}; } catch { /* non-JSON */ }
    throw new ApiError(e.code ?? "http_error", e.message ?? `Request failed (${res.status}).`, e.request_id);
  }
  return (text ? await res.text() : await res.json()) as T;
}
export const api = {
  config: () => call<AppConfig>("/ui/config"),
  verify: (answer: string) => call<Verification>("/ui/verify", { method: "POST", body: JSON.stringify({ answer }) }),
  get: (id: string) => call<Verification>(`/ui/verify/${encodeURIComponent(id)}`),
  report: (id: string) => call<string>(`/ui/verify/${encodeURIComponent(id)}/report`, undefined, true),
  history: (p: { q?: string; status?: string; since?: string }) => {
    const qs = new URLSearchParams(Object.entries(p).filter(([, v]) => v) as [string, string][]).toString();
    return call<{ items: HistoryItem[] }>(`/ui/history${qs ? "?" + qs : ""}`);
  },
};
