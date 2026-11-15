import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ClaimCard from "./ClaimCard";
import type { ClaimResult } from "../types";

const r: ClaimResult = { claim: { id: "c1", original_text: "Acme Pro costs $20.", normalized: "Acme Pro costs $20.", category: "Pricing / Financial", entities: [], dates: [], numbers: [], volatility: "high", time_sensitive: true },
  status: "STALE", freshness_score: null, evidence_confidence: 0.5, source_reliability: 0.9, explanation: "Newer evidence conflicts.", conflict: false, suggested_correction: "Acme Pro costs $29.", alerts: [], queries: [],
  sources: [{ title: "Pricing", url: "https://a.example/p", domain: "a.example", published_date: null, published_date_inferred: false, retrieved_at: "2026-11-12T00:00:00Z", excerpt: "Now $29", source_type: "official_docs", authority: 0.9, relevance: 0.9, stance: "contradicts", from_cache: false, simulated: true }] };

describe("ClaimCard", () => {
  it("renders status, no invented freshness, and expands evidence", () => {
    render(<ClaimCard r={r} />);
    expect(screen.getByText("Stale")).toBeTruthy();
    expect(screen.getByText("Not established")).toBeTruthy();
    expect(screen.queryByText("Now $29")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /show evidence/i }));
    expect(screen.getByText("Now $29")).toBeTruthy();
    expect(screen.getByText(/SIMULATED/)).toBeTruthy();
    expect(screen.getByText(/date unknown/)).toBeTruthy();
  });

  it("labels inferred source dates", () => {
    const inferred = { ...r, sources: [{ ...r.sources[0], published_date: "2026-11-10", published_date_inferred: true }] };
    render(<ClaimCard r={inferred} />);
    fireEvent.click(screen.getByRole("button", { name: /show evidence/i }));
    expect(screen.getByText(/2026-11-10 \(inferred\)/)).toBeTruthy();
  });
});
