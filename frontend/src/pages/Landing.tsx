import { Link } from "react-router-dom";
import type { AppConfig } from "../types";

const steps = [["Extract", "Splits an answer into independent factual claims and skips opinions."],
  ["Research", "Runs targeted Tavily searches per claim, not per paragraph."],
  ["Evaluate", "Compares retrieved evidence to the claim, weighing authority, dates and agreement."],
  ["Correct", "Rebuilds the answer with citations, flagging anything unresolved."]];
const features = [["Claim-level freshness", "Every claim gets its own status, freshness, evidence confidence and source reliability. They are never merged into one trust score."],
  ["Volatility-aware", "Prices age faster than historical dates, so each claim type has its own freshness half-life."],
  ["Conflict intelligence", "When credible sources disagree, both sides are shown and no verdict is forced."],
  ["Traceable evidence", "Every verdict links to the sources, excerpts, publication dates and retrieval times behind it."]];

export default function Landing({ cfg }: { cfg: AppConfig | null }) {
  return (
    <div className="space-y-16">
      <section className="pt-6 max-w-3xl">
        <p className="text-accent text-sm font-medium">AI answer verification · information freshness</p>
        <h1 className="mt-3 text-4xl md:text-5xl font-semibold text-white leading-tight">The Intelligence Layer That Keeps AI Answers Fresh.</h1>
        <p className="mt-4 text-slate-300 text-lg">An AI answer is not trustworthy simply because it sounds confident. TruthGuard checks each important claim against live web evidence and shows how current it is.</p>
        <div className="mt-6 flex gap-3"><Link to="/workspace" className="btn btn-primary">Open workspace</Link><Link to="/developers" className="btn btn-ghost">Developer API</Link></div>
        {cfg?.mode === "demo" && <p className="mt-3 text-xs text-amber-300">Running in demo mode with simulated sources.</p>}
      </section>
      <section><h2 className="text-xl font-semibold text-white mb-2">The problem</h2>
        <p className="text-slate-300 max-w-3xl">LLM applications confidently repeat facts that have changed: prices, API versions, laws, company leadership. A single trust score hides which statement is stale. TruthGuard flags the exact claim and shows the evidence.</p></section>
      <section><h2 className="text-xl font-semibold text-white mb-4">How it works</h2>
        <div className="grid md:grid-cols-4 gap-3">{steps.map(([t, d], i) => <div key={t} className="card p-4"><div className="text-accent text-sm">Step {i + 1}</div><h3 className="text-white font-medium">{t}</h3><p className="text-sm text-slate-400 mt-1">{d}</p></div>)}</div></section>
      <section><h2 className="text-xl font-semibold text-white mb-4">Features</h2>
        <div className="grid md:grid-cols-2 gap-3">{features.map(([t, d]) => <div key={t} className="card p-4"><h3 className="text-white font-medium">{t}</h3><p className="text-sm text-slate-400 mt-1">{d}</p></div>)}</div></section>
      <section className="card p-5"><h2 className="text-xl font-semibold text-white mb-2">Illustrative example <span className="text-xs text-amber-300">(simulated, not a live result)</span></h2>
        <p className="text-sm text-slate-300">“Acme Cloud Pro costs $20 per month.” → a newer official pricing page shows $29 → status <b>Stale</b>, with the source, its date and a corrected, cited sentence. <Link className="text-accent underline" to="/workspace">Try it in the workspace.</Link></p></section>
      <section className="grid md:grid-cols-2 gap-3">
        <div className="card p-5"><h2 className="text-white font-medium">Developer integration</h2><p className="text-sm text-slate-400 mt-1">Call <code>POST /api/v1/verify</code> after your LLM responds. API-key auth, rate limits, request IDs, OpenAPI docs at <code>/docs</code>.</p></div>
        <div className="card p-5"><h2 className="text-white font-medium">Security and privacy</h2><p className="text-sm text-slate-400 mt-1">Keys stay on the server. Retrieved pages are treated as untrusted data, sensitive tokens are redacted, and history is deleted after the retention period.</p></div>
      </section>
    </div>
  );
}
