export type Status = "VERIFIED_CURRENT" | "POTENTIALLY_OUTDATED" | "CONTRADICTED" | "UNVERIFIABLE" | "STALE" | "NOT_TIME_SENSITIVE" | "INSUFFICIENT_EVIDENCE";
export interface Source { title: string; url: string; domain: string; published_date: string | null; published_date_inferred: boolean; retrieved_at: string; excerpt: string;
  source_type: string; authority: number; relevance: number; stance: "supports" | "contradicts" | "neutral"; from_cache: boolean; simulated: boolean; }
export interface Claim { id: string; original_text: string; normalized: string; category: string; entities: string[]; dates: string[]; numbers: string[]; volatility: string; time_sensitive: boolean; }
export interface ClaimResult { claim: Claim; status: Status; freshness_score: number | null; evidence_confidence: number; source_reliability: number;
  explanation: string; sources: Source[]; conflict: boolean; suggested_correction: string | null; alerts: string[]; queries: string[]; }
export interface Verification { id: string; created_at: string; mode: "live" | "demo"; notice: string; answer: string; as_of: string; claims: ClaimResult[];
  summary: { total_claims: number; counts: Record<string, number>; evidence_coverage: number | null; needs_attention: number };
  verified_answer: string | null; changes: { claim_id: string; type: string; before: string; after: string }[]; warnings: string[]; }
export interface HistoryItem { id: string; created_at: string; mode: string; statuses: string; preview: string; }
export interface AppConfig { mode: "live" | "demo"; llm: string; cache_ttl_seconds: number; rate_limit_per_min: number; retention_days: number;
  concurrency: number; demo_answer: string; tavily_configured: boolean; version: string; }
