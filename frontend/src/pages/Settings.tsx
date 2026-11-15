import type { AppConfig } from "../types";
const policy = [["Stock prices / breaking news", "very high", "1 day"], ["Prices, API and software versions", "high", "30 days"], ["Leadership, statistics, regulations", "medium", "180 days"],
  ["Slow-changing facts", "low", "3 years"], ["Stable facts (math, history)", "stable", "not re-checked"]];
export default function Settings({ cfg }: { cfg: AppConfig | null }) {
  if (!cfg) return <div className="card p-6 text-slate-400">Settings could not be loaded. Is the backend running?</div>;
  const rows = [["Verification mode", cfg.mode === "live" ? "Live (Tavily)" : "Demo (simulated sources)"], ["Tavily API key", cfg.tavily_configured ? "Configured on server" : "Not configured"],
    ["LLM provider", cfg.llm], ["Search cache expiry", `${cfg.cache_ttl_seconds} s`], ["Parallel claim research", String(cfg.concurrency)],
    ["API rate limit", `${cfg.rate_limit_per_min} / minute`], ["History retention", cfg.retention_days > 0 ? `${cfg.retention_days} days` : "Kept indefinitely"], ["Server version", cfg.version]];
  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-semibold text-white">Settings</h1>
      <p className="text-sm text-slate-400">These values are read-only here. Secrets and policies are set by the server operator through environment variables (see <code>.env.example</code>) so that nothing sensitive passes through the browser.</p>
      <div className="card divide-y divide-ink-600/60">{rows.map(([k, v]) => <div key={k} className="p-3 flex justify-between text-sm"><span className="text-slate-400">{k}</span><span className="text-white">{v}</span></div>)}</div>
      <section><h2 className="text-white font-medium mb-2">Freshness policy (default heuristics)</h2>
        <div className="card overflow-x-auto"><table className="w-full text-sm"><thead className="text-left text-slate-400"><tr><th className="p-3">Information</th><th>Volatility</th><th>Half-life</th></tr></thead>
          <tbody>{policy.map(([a, b, c]) => <tr key={a} className="border-t border-ink-600/60"><td className="p-3">{a}</td><td>{b}</td><td>{c}</td></tr>)}</tbody></table></div>
        <p className="text-xs text-slate-500 mt-2">Heuristics, not guaranteed expiry periods. Source priority: government → official company → official docs → research → news → secondary.</p></section>
    </div>
  );
}
