import { useMemo, useState } from "react";
import type { Verification } from "../types";
import { diffWords, download, type Seg } from "../utils";
import { api } from "../api";

const cls = { same: "", removed: "bg-rose-500/25 line-through", added: "bg-emerald-500/25" };
const Render = ({ segs }: { segs: Seg[] }) => <>{segs.map((s, i) => <span key={i} className={cls[s.kind]}>{s.text}</span>)}</>;

export default function VerifiedAnswer({ v }: { v: Verification }) {
  const [copied, setCopied] = useState(false);
  const [err, setErr] = useState("");
  const d = useMemo(() => diffWords(v.answer, v.verified_answer ?? v.answer), [v]);
  async function copy() {
    try { await navigator.clipboard.writeText(v.verified_answer ?? ""); setCopied(true); setTimeout(() => setCopied(false), 1500); }
    catch { setErr("Copy is blocked by the browser. Select the text and copy manually."); }
  }
  async function exportReport() {
    try { download(`truthguard-${v.id}.md`, await api.report(v.id)); } catch (e: any) { setErr(e.message); }
  }
  return (
    <section aria-label="Verified answer" className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-white">Original vs verified answer</h2>
        <div className="flex gap-2"><button className="btn btn-ghost" onClick={copy}>{copied ? "Copied" : "Copy verified answer"}</button>
          <button className="btn btn-ghost" onClick={exportReport}>Export report (.md)</button></div>
      </div>
      {err && <p role="alert" className="text-sm text-rose-300">{err}</p>}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="card p-4"><h3 className="text-xs uppercase text-slate-400 mb-2">Original</h3><p className="whitespace-pre-wrap text-sm leading-relaxed"><Render segs={d.left} /></p></div>
        <div className="card p-4"><h3 className="text-xs uppercase text-slate-400 mb-2">Verified (as of {v.as_of})</h3><p className="whitespace-pre-wrap text-sm leading-relaxed"><Render segs={d.right} /></p></div>
      </div>
      {v.changes.length === 0 ? <p className="text-sm text-slate-400">No changes were needed or possible.</p> :
        <ul className="text-sm space-y-1">{v.changes.map((c) => <li key={c.claim_id}><b className="capitalize">{c.type}:</b> <span className="text-slate-400">{c.before}</span></li>)}</ul>}
    </section>
  );
}
