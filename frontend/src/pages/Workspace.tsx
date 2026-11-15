import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, ApiError } from "../api";
import type { AppConfig, Status, Verification } from "../types";
import { MAX_CHARS, STATUS, filterClaims, validateInput } from "../utils";
import Dashboard from "../components/Dashboard";
import ClaimCard from "../components/ClaimCard";
import VerifiedAnswer from "../components/VerifiedAnswer";

const EXAMPLES = [
  ["Software & pricing", "The latest stable release of Python is 3.9. Acme Cloud Pro costs $20 per month."],
  ["Conflicting sources", "Acme Cloud has 10,000 employees. Water boils at 100 degrees Celsius at sea level."],
];

export default function Workspace({ cfg }: { cfg: AppConfig | null }) {
  const { id } = useParams(); const nav = useNavigate();
  const [text, setText] = useState(""); const [touched, setTouched] = useState(false);
  const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null);
  const [v, setV] = useState<Verification | null>(null); const [filter, setFilter] = useState("ALL");
  const invalid = validateInput(text);

  useEffect(() => {
    if (!id) { setV(null); return; }
    setBusy(true); setError(null);
    api.get(id).then((r) => { setV(r); setText(r.answer); }).catch((e: ApiError) => setError(e.message)).finally(() => setBusy(false));
  }, [id]);

  async function run() {
    setTouched(true); if (invalid) return;
    setBusy(true); setError(null); setV(null);
    try { const r = await api.verify(text.trim()); setV(r); nav(`/workspace/${r.id}`, { replace: true }); }
    catch (e: any) { setError(e.message + (e.requestId ? ` (request ${e.requestId})` : "")); }
    finally { setBusy(false); }
  }

  return (
    <div className="space-y-8">
      <section className="card p-5 space-y-3">
        <label htmlFor="answer" className="text-white font-medium">Paste an AI-generated answer</label>
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map(([l, t]) => <button key={l} className="btn btn-ghost text-xs" onClick={() => { setText(t); setTouched(false); }}>Example: {l}</button>)}
          {cfg?.demo_answer && <button className="btn btn-ghost text-xs" onClick={() => setText(cfg.demo_answer)}>Full demo answer</button>}
        </div>
        <textarea id="answer" value={text} onChange={(e) => setText(e.target.value)} onBlur={() => setTouched(true)} rows={7} maxLength={MAX_CHARS + 500}
          aria-invalid={touched && !!invalid} aria-describedby="answer-help"
          className="w-full rounded-lg bg-ink-950 border border-ink-600 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent" placeholder="e.g. The latest version of Python is 3.11 and Company X has 10,000 employees." />
        <div id="answer-help" className="flex justify-between text-xs">
          <span className={touched && invalid ? "text-rose-300" : "text-slate-500"} role={touched && invalid ? "alert" : undefined}>{touched && invalid ? invalid : "Each factual claim is researched and scored separately."}</span>
          <span className="text-slate-500">{text.trim().length}/{MAX_CHARS}</span>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn btn-primary" onClick={run} disabled={busy}>{busy ? "Verifying…" : "Verify claims"}</button>
          {busy && <span className="text-xs text-slate-400" role="status">Running on the server: extract claims → research each claim → score evidence. This can take several seconds.</span>}
        </div>
      </section>

      {error && <div role="alert" className="card p-4 border-rose-500/50 text-rose-200">{error}</div>}
      {!v && !busy && !error && <div className="card p-8 text-center text-slate-400">No results yet. Submit an answer above, or load one from <a className="text-accent underline" href="#/history">History</a>.</div>}

      {v && (<>
        <p className="text-xs text-slate-400">{v.notice}</p>
        {v.warnings.map((w) => <p key={w} className="text-xs text-amber-300">{w}</p>)}
        <Dashboard v={v} />
        <section aria-label="Claim explorer" className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-white">Claim explorer</h2>
            <select aria-label="Filter by status" value={filter} onChange={(e) => setFilter(e.target.value)} className="rounded-lg bg-ink-900 border border-ink-600 px-2 py-1.5 text-sm">
              <option value="ALL">All statuses</option>
              {Object.keys(STATUS).map((s) => <option key={s} value={s}>{STATUS[s as Status].label}</option>)}
            </select>
          </div>
          {v.claims.length === 0 && <p className="card p-4 text-slate-400">No verifiable factual claims were found in this text.</p>}
          {filterClaims(v.claims, filter).map((c) => <ClaimCard key={c.claim.id} r={c} />)}
        </section>
        <VerifiedAnswer v={v} />
      </>)}
    </div>
  );
}
