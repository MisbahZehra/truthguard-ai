import json, sqlite3, threading
from .schemas import VerificationResult


class Store:
    """SQLite persistence with parameterized queries only (no string-built SQL)."""

    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        self.db.execute("CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, "
                        "statuses TEXT, preview TEXT, data TEXT)")

    def save(self, r: VerificationResult):
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO sessions VALUES(?,?,?,?,?,?)",
                            (r.id, r.created_at.isoformat(), r.mode, ",".join(sorted({c.status.value for c in r.claims})),
                             r.answer[:120], r.model_dump_json()))
            self.db.commit()

    def get(self, id: str) -> VerificationResult | None:
        row = self.db.execute("SELECT data FROM sessions WHERE id=?", (id,)).fetchone()
        return VerificationResult.model_validate_json(row[0]) if row else None

    def history(self, q: str | None = None, status: str | None = None, since: str | None = None, limit: int = 50):
        sql, args = "SELECT id, created_at, mode, statuses, preview FROM sessions WHERE 1=1", []
        if q:
            sql += " AND preview LIKE ?"; args.append(f"%{q}%")
        if status:
            sql += " AND statuses LIKE ?"; args.append(f"%{status}%")
        if since:
            sql += " AND created_at >= ?"; args.append(since)
        sql += " ORDER BY created_at DESC LIMIT ?"; args.append(min(limit, 200))
        return [dict(zip(("id", "created_at", "mode", "statuses", "preview"), r)) for r in self.db.execute(sql, args)]

    def purge(self, before_iso: str) -> int:
        with self.lock:
            n = self.db.execute("DELETE FROM sessions WHERE created_at < ?", (before_iso,)).rowcount
            self.db.commit()
            return n
