import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Verification } from "../types";
import { STATUS, fmt, summaryLabel } from "../utils";

const COLORS: Record<string, string> = { VERIFIED_CURRENT: "#34d399", POTENTIALLY_OUTDATED: "#fbbf24", CONTRADICTED: "#fb7185", UNVERIFIABLE: "#94a3b8",
  STALE: "#f87171", NOT_TIME_SENSITIVE: "#38bdf8", INSUFFICIENT_EVIDENCE: "#a78bfa" };

export default function Dashboard({ v }: { v: Verification }) {
  const c = v.summary.counts;
  const data = Object.entries(c).map(([k, n]) => ({ key: k, name: STATUS[k as keyof typeof STATUS].label, n }));
  const stats = [["Claims extracted", v.summary.total_claims], ["Verified current", c.VERIFIED_CURRENT ?? 0],
    ["Potentially outdated / stale", (c.POTENTIALLY_OUTDATED ?? 0) + (c.STALE ?? 0)], ["Contradicted", c.CONTRADICTED ?? 0],
    ["Unverifiable / insufficient", (c.UNVERIFIABLE ?? 0) + (c.INSUFFICIENT_EVIDENCE ?? 0)]];
  return (
    <section aria-label="Results dashboard" className="space-y-4">
      <div className="card p-5">
        <p className="text-white font-medium">{summaryLabel(v)}</p>
        <p className="text-xs text-slate-400 mt-1">
          Verified {fmt(v.created_at)} · as-of {v.as_of} · mode {v.mode.toUpperCase()} · evidence coverage{" "}
          {v.summary.evidence_coverage === null ? "n/a" : `${Math.round(v.summary.evidence_coverage * 100)}% of checked claims`}
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {stats.map(([l, n]) => (<div key={l as string} className="card p-4"><div className="text-2xl font-semibold text-white">{n}</div><div className="text-xs text-slate-400">{l}</div></div>))}
      </div>
      {data.length > 0 && (
        <div className="card p-4 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 40 }}>
              <XAxis type="number" allowDecimals={false} stroke="#64748b" /><YAxis type="category" dataKey="name" width={150} stroke="#94a3b8" fontSize={12} />
              <Tooltip cursor={{ fill: "#1e2b47" }} contentStyle={{ background: "#0f172a", border: "1px solid #2b3a5c" }} />
              <Bar dataKey="n" radius={4}>{data.map((d) => <Cell key={d.key} fill={COLORS[d.key]} />)}</Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
