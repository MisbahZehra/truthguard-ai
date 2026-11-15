import { useState } from "react";
import type { ClaimResult } from "../types";
import StatusBadge from "./StatusBadge";

const stanceCls = { supports: "text-emerald-300", contradicts: "text-rose-300", neutral: "text-slate-400" };

export default function ClaimCard({ r }: { r: ClaimResult }) {
  const [open, setOpen] = useState(false);
  const id = `claim-${r.claim.id}`;
  return (
    <article className="card p-4" data-testid="claim-card">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-white">{r.claim.original_text}</p>
          {r.claim.normalized !== r.claim.original_text && <p className="text-xs text-slate-400 mt-1">Normalized: {r.claim.normalized}</p>}
        </div>
        <StatusBadge status={r.status} />
      </div>
      <dl className="mt-3 grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
        <Metric label="Freshness" value={r.freshness_score === null ? "Not established" : `${r.freshness_score}/100`} note="How current the evidence looks" />
        <Metric label="Evidence confidence" value={r.evidence_confidence.toFixed(2)} note="Not a probability of truth" />
        <Metric label="Source reliability" value={r.source_reliability.toFixed(2)} note="Authority of sources used" />
        <Metric label="Volatility" value={r.claim.volatility.replace("_", " ")} note="Typical change rate" />
        <Metric label="Category" value={r.claim.category} />
      </dl>
      <p className="mt-3 text-sm text-slate-300">{r.explanation}</p>
      {r.alerts.length > 0 && <ul className="mt-2 text-xs text-amber-300 list-disc pl-5">{r.alerts.map((a) => <li key={a}>{a}</li>)}</ul>}
      {r.suggested_correction && <p className="mt-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-3 text-sm"><b>Suggested correction:</b> {r.suggested_correction}</p>}
      <button className="btn btn-ghost mt-3" aria-expanded={open} aria-controls={id} onClick={() => setOpen(!open)}>
        {open ? "Hide evidence" : `Show evidence (${r.sources.length})`}
      </button>
      {open && (
        <div id={id} className="mt-3 space-y-3">
          {r.queries.length > 0 && <p className="text-xs text-slate-400">Queries: {r.queries.map((q) => `“${q}”`).join(" · ")}</p>}
          {r.sources.length === 0 && <p className="text-sm text-slate-400">No sources were retrieved.</p>}
          {r.sources.map((s) => (
            <div key={s.url} className="rounded-lg border border-ink-600 p-3 text-sm">
              <div className="flex flex-wrap justify-between gap-2">
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-accent underline break-all">{s.title}</a>
                <span className={`text-xs font-medium ${stanceCls[s.stance]}`}>{s.stance}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {s.domain} · {s.source_type.replace("_", " ")} · authority {s.authority.toFixed(2)} · published {s.published_date ?? "date unknown"}{s.published_date_inferred ? " (inferred)" : ""} · retrieved {new Date(s.retrieved_at).toLocaleString()}
                {s.from_cache && " (cached)"}{s.simulated && <b className="text-amber-300"> · SIMULATED demo source</b>}
              </p>
              <blockquote className="mt-2 text-slate-300 border-l-2 border-ink-600 pl-3">{s.excerpt}</blockquote>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}
function Metric({ label, value, note }: { label: string; value: string; note?: string }) {
  return <div title={note}><dt className="text-slate-500">{label}</dt><dd className="text-slate-100 font-medium capitalize">{value}</dd></div>;
}
