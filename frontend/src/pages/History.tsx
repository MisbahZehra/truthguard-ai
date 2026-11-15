import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { HistoryItem } from "../types";
import { STATUS, fmt } from "../utils";

export default function History() {
  const [items, setItems] = useState<HistoryItem[] | null>(null);
  const [q, setQ] = useState(""); const [status, setStatus] = useState(""); const [since, setSince] = useState("");
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const t = setTimeout(() => { setError(null); api.history({ q, status, since }).then((r) => setItems(r.items)).catch((e) => setError(e.message)); }, 250);
    return () => clearTimeout(t);
  }, [q, status, since]);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-white">History</h1>
      <div className="card p-4 flex flex-wrap gap-3">
        <input aria-label="Search history" placeholder="Search answers" value={q} onChange={(e) => setQ(e.target.value)} className="flex-1 min-w-48 rounded-lg bg-ink-950 border border-ink-600 px-3 py-1.5 text-sm" />
        <select aria-label="Status filter" value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-lg bg-ink-950 border border-ink-600 px-2 py-1.5 text-sm">
          <option value="">Any status</option>{Object.entries(STATUS).map(([k, m]) => <option key={k} value={k}>{m.label}</option>)}</select>
        <input aria-label="Since date" type="date" value={since} onChange={(e) => setSince(e.target.value)} className="rounded-lg bg-ink-950 border border-ink-600 px-2 py-1.5 text-sm" />
      </div>
      {error && <p role="alert" className="text-rose-300 text-sm">{error}</p>}
      {items === null && !error && <p className="text-slate-400">Loading…</p>}
      {items?.length === 0 && <div className="card p-8 text-center text-slate-400">No saved verifications match. <Link className="text-accent underline" to="/workspace">Run one</Link>.</div>}
      <ul className="space-y-2">{items?.map((i) => (
        <li key={i.id}><Link to={`/workspace/${i.id}`} className="card p-4 block hover:border-accent/60">
          <div className="flex justify-between gap-2 text-xs text-slate-400"><span>{fmt(i.created_at)}</span><span className={i.mode === "demo" ? "text-amber-300" : ""}>{i.mode.toUpperCase()}</span></div>
          <p className="text-white mt-1 truncate">{i.preview}</p>
          <p className="text-xs text-slate-400 mt-1">{i.statuses.split(",").map((s) => STATUS[s as keyof typeof STATUS]?.label ?? s).join(" · ")}</p></Link></li>))}</ul>
    </div>
  );
}
