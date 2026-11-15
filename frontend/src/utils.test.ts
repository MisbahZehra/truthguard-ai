import { describe, expect, it, vi } from "vitest";
import { diffWords, filterClaims, validateInput, MAX_CHARS } from "./utils";
import { api, ApiError } from "./api";

describe("input validation", () => {
  it("rejects short and oversized input", () => {
    expect(validateInput("hi")).toMatch(/at least/);
    expect(validateInput("x".repeat(MAX_CHARS + 1))).toMatch(/limited/);
    expect(validateInput("Python 3.9 is the latest release.")).toBeNull();
  });
});
describe("diff", () => {
  it("marks removed and added words", () => {
    const d = diffWords("costs $20 per month", "costs $29 per month");
    expect(d.left.find((s) => s.kind === "removed")?.text).toBe("$20");
    expect(d.right.find((s) => s.kind === "added")?.text).toBe("$29");
  });
  it("identical text has no changes", () => {
    expect(diffWords("a b", "a b").left.every((s) => s.kind === "same")).toBe(true);
  });
});
describe("filters", () => {
  it("filters claims by status", () => {
    const items = [{ status: "STALE" }, { status: "VERIFIED_CURRENT" }];
    expect(filterClaims(items, "STALE")).toHaveLength(1);
    expect(filterClaims(items, "ALL")).toHaveLength(2);
  });
});
describe("api errors", () => {
  it("surfaces structured server errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 429, json: async () => ({ error: { code: "rate_limited", message: "Slow down", request_id: "r1" } }) }));
    await expect(api.verify("some long enough answer")).rejects.toMatchObject({ code: "rate_limited", message: "Slow down" });
  });
  it("reports network failure clearly", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("down")));
    await expect(api.history({})).rejects.toBeInstanceOf(ApiError);
  });
});
