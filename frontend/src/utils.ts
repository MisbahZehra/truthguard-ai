import type { Status, Verification } from "./types";
export const STATUS: Record<Status, { label: string; cls: string; hint: string }> = {
  VERIFIED_CURRENT: { label: "Verified current", cls: "bg-emerald-500/15 text-emerald-300 border-emerald-500/40", hint: "Evidence supports the claim; nothing newer contradicts it." },
  POTENTIALLY_OUTDATED: { label: "Potentially outdated", cls: "bg-amber-500/15 text-amber-300 border-amber-500/40", hint: "May once have been right; newer or weaker evidence suggests an update." },
  CONTRADICTED: { label: "Contradicted", cls: "bg-rose-500/15 text-rose-300 border-rose-500/40", hint: "Relevant evidence conflicts with the claim." },
  UNVERIFIABLE: { label: "Unverifiable", cls: "bg-slate-500/20 text-slate-300 border-slate-500/40", hint: "Not enough reliable evidence to confirm or reject." },
  STALE: { label: "Stale", cls: "bg-red-500/15 text-red-300 border-red-500/40", hint: "Demonstrably outdated per newer authoritative evidence." },
  NOT_TIME_SENSITIVE: { label: "Not time-sensitive", cls: "bg-sky-500/15 text-sky-300 border-sky-500/40", hint: "A stable fact; no frequent re-checking needed." },
  INSUFFICIENT_EVIDENCE: { label: "Insufficient evidence", cls: "bg-violet-500/15 text-violet-300 border-violet-500/40", hint: "Evidence is incomplete, ambiguous or conflicting." },
};
export const MAX_CHARS = 8000, MIN_CHARS = 10;
export function validateInput(t: string): string | null {
  const n = t.trim().length;
  if (n < MIN_CHARS) return `Enter at least ${MIN_CHARS} characters.`;
  if (n > MAX_CHARS) return `Input is limited to ${MAX_CHARS} characters (currently ${n}).`;
  return null;
}
export type Seg = { text: string; kind: "same" | "removed" | "added" };
/** Word-level LCS diff used for the original-vs-verified comparison. */
export function diffWords(a: string, b: string): { left: Seg[]; right: Seg[] } {
  const x = a.split(/(\s+)/), y = b.split(/(\s+)/);
  const dp = Array.from({ length: x.length + 1 }, () => new Array(y.length + 1).fill(0));
  for (let i = x.length - 1; i >= 0; i--) for (let j = y.length - 1; j >= 0; j--)
    dp[i][j] = x[i] === y[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const left: Seg[] = [], right: Seg[] = []; let i = 0, j = 0;
  while (i < x.length && j < y.length) {
    if (x[i] === y[j]) { left.push({ text: x[i], kind: "same" }); right.push({ text: y[j], kind: "same" }); i++; j++; }
    else if (dp[i + 1][j] >= dp[i][j + 1]) left.push({ text: x[i++], kind: "removed" });
    else right.push({ text: y[j++], kind: "added" });
  }
  while (i < x.length) left.push({ text: x[i++], kind: "removed" });
  while (j < y.length) right.push({ text: y[j++], kind: "added" });
  return { left, right };
}
export function filterClaims<T extends { status: string }>(items: T[], status: string): T[] {
  return status === "ALL" ? items : items.filter((i) => i.status === status);
}
export function download(name: string, text: string, type = "text/markdown") {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a"); a.href = url; a.download = name; a.click(); URL.revokeObjectURL(url);
}
export const fmt = (iso: string) => new Date(iso).toLocaleString();
export function summaryLabel(v: Verification): string {
  const n = v.summary.needs_attention;
  return n === 0 ? "No claims need attention based on available evidence." : `${n} of ${v.summary.total_claims} claims need attention.`;
}
