import { NavLink, Route, Routes, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "./api";
import type { AppConfig } from "./types";
import Landing from "./pages/Landing";
import Workspace from "./pages/Workspace";
import History from "./pages/History";
import Developer from "./pages/Developer";
import Settings from "./pages/Settings";

const nav = [["/workspace", "Workspace"], ["/history", "History"], ["/developers", "Developers"], ["/settings", "Settings"]];

export default function App() {
  const [cfg, setCfg] = useState<AppConfig | null>(null);
  useEffect(() => { api.config().then(setCfg).catch(() => setCfg(null)); }, []);
  return (
    <div className="min-h-screen flex flex-col">
      {cfg?.mode === "demo" && (
        <div role="status" className="bg-amber-400 text-ink-950 text-center text-sm py-1.5 px-3 font-medium">
          DEMO MODE — all sources are simulated and are not live Tavily results. Configure TAVILY_API_KEY for live verification.
        </div>
      )}
      <header className="border-b border-ink-600/60 bg-ink-900/80">
        <div className="mx-auto max-w-6xl px-4 h-14 flex items-center gap-6">
          <Link to="/" className="font-semibold text-white tracking-tight">TruthGuard<span className="text-accent"> AI</span></Link>
          <nav className="flex gap-1 text-sm overflow-x-auto">
            {nav.map(([to, label]) => (
              <NavLink key={to} to={to} className={({ isActive }) => `px-3 py-1.5 rounded-md ${isActive ? "bg-ink-700 text-white" : "text-slate-400 hover:text-white"}`}>{label}</NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Landing cfg={cfg} />} />
          <Route path="/workspace" element={<Workspace cfg={cfg} />} />
          <Route path="/workspace/:id" element={<Workspace cfg={cfg} />} />
          <Route path="/history" element={<History />} />
          <Route path="/developers" element={<Developer />} />
          <Route path="/settings" element={<Settings cfg={cfg} />} />
          <Route path="*" element={<div className="card p-8">Page not found. <Link className="text-accent underline" to="/">Go home</Link></div>} />
        </Routes>
      </main>
      <footer className="border-t border-ink-600/60 text-xs text-slate-500 py-5 text-center px-4">
        Evidence-based verification using available sources at the time of checking. TruthGuard does not guarantee truth.
      </footer>
    </div>
  );
}
