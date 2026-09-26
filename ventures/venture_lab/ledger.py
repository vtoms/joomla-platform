"""SQLite ledger: experiment state, runs and API spend, KPIs, approvals, learnings."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiment_state (
    experiment TEXT PRIMARY KEY,
    status TEXT NOT NULL,             -- proposed | active | paused | killed | scaling
    phase_index INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    updated_at TEXT NOT NULL,
    note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment TEXT NOT NULL,
    kind TEXT NOT NULL,               -- agent | batch | portfolio
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,             -- running | ok | budget_stop | error | refused
    model TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    summary TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment TEXT NOT NULL,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    source TEXT NOT NULL,             -- agent | human | integration
    note TEXT DEFAULT '',
    ts TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL,            -- JSON
    one_time_usd REAL DEFAULT 0,
    monthly_usd REAL DEFAULT 0,
    status TEXT NOT NULL,             -- pending | approved | rejected | executed
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decision_note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS learnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment TEXT NOT NULL,
    text TEXT NOT NULL,
    ts TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def month_start() -> str:
    today = datetime.now(UTC)
    return today.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def _rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    # -- experiment state -------------------------------------------------
    def get_state(self, experiment: str) -> dict[str, Any] | None:
        rows = self._rows("SELECT * FROM experiment_state WHERE experiment = ?", (experiment,))
        return rows[0] if rows else None

    def set_state(
        self,
        experiment: str,
        *,
        status: str | None = None,
        phase_index: int | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        current = self.get_state(experiment)
        if current is None:
            current = {"status": "proposed", "phase_index": 0, "started_at": None, "note": ""}
        new_status = status or current["status"]
        started_at = current["started_at"]
        if new_status == "active" and not started_at:
            started_at = now()
        self.conn.execute(
            """INSERT INTO experiment_state (experiment, status, phase_index, started_at, updated_at, note)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(experiment) DO UPDATE SET
                 status = excluded.status, phase_index = excluded.phase_index,
                 started_at = excluded.started_at, updated_at = excluded.updated_at,
                 note = excluded.note""",
            (
                experiment,
                new_status,
                current["phase_index"] if phase_index is None else phase_index,
                started_at,
                now(),
                current["note"] if note is None else note,
            ),
        )
        self.conn.commit()
        return self.get_state(experiment)  # type: ignore[return-value]

    def all_states(self) -> dict[str, dict[str, Any]]:
        return {r["experiment"]: r for r in self._rows("SELECT * FROM experiment_state")}

    # -- runs & spend -----------------------------------------------------
    def start_run(self, experiment: str, kind: str, model: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO runs (experiment, kind, started_at, status, model) VALUES (?, ?, ?, 'running', ?)",
            (experiment, kind, now(), model),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def add_usage(self, run_id: int, usage: Any, cost_usd: float) -> None:
        def g(name: str) -> int:
            return int(getattr(usage, name, 0) or 0) if usage is not None else 0

        self.conn.execute(
            """UPDATE runs SET input_tokens = input_tokens + ?, output_tokens = output_tokens + ?,
                 cache_read_tokens = cache_read_tokens + ?, cache_write_tokens = cache_write_tokens + ?,
                 cost_usd = cost_usd + ? WHERE id = ?""",
            (
                g("input_tokens"),
                g("output_tokens"),
                g("cache_read_input_tokens"),
                g("cache_creation_input_tokens"),
                cost_usd,
                run_id,
            ),
        )
        self.conn.commit()

    def finish_run(self, run_id: int, status: str, summary: str) -> None:
        self.conn.execute(
            "UPDATE runs SET finished_at = ?, status = ?, summary = ? WHERE id = ?",
            (now(), status, summary, run_id),
        )
        self.conn.commit()

    def run(self, run_id: int) -> dict[str, Any]:
        return self._rows("SELECT * FROM runs WHERE id = ?", (run_id,))[0]

    def recent_runs(self, experiment: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        if experiment:
            return self._rows("SELECT * FROM runs WHERE experiment = ? ORDER BY id DESC LIMIT ?", (experiment, limit))
        return self._rows("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))

    def last_run_at(self, experiment: str, kind: str = "agent") -> str | None:
        rows = self._rows(
            "SELECT started_at FROM runs WHERE experiment = ? AND kind = ? ORDER BY id DESC LIMIT 1",
            (experiment, kind),
        )
        return rows[0]["started_at"] if rows else None

    def spend_this_month(self, experiment: str | None = None) -> float:
        if experiment:
            row = self.conn.execute(
                "SELECT COALESCE(SUM(cost_usd), 0) FROM runs WHERE experiment = ? AND started_at >= ?",
                (experiment, month_start()),
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT COALESCE(SUM(cost_usd), 0) FROM runs WHERE started_at >= ?", (month_start(),)
            ).fetchone()
        return float(row[0])

    # -- metrics ----------------------------------------------------------
    def record_metric(self, experiment: str, name: str, value: float, source: str, note: str = "") -> None:
        self.conn.execute(
            "INSERT INTO metrics (experiment, name, value, source, note, ts) VALUES (?, ?, ?, ?, ?, ?)",
            (experiment, name, float(value), source, note, now()),
        )
        self.conn.commit()

    def latest_metrics(self, experiment: str) -> dict[str, dict[str, Any]]:
        """Most recent value per metric name."""
        rows = self._rows(
            """SELECT m.* FROM metrics m JOIN (
                 SELECT name, MAX(id) AS id FROM metrics WHERE experiment = ? GROUP BY name
               ) latest ON m.id = latest.id ORDER BY m.name""",
            (experiment,),
        )
        return {r["name"]: r for r in rows}

    # -- approvals --------------------------------------------------------
    def add_approval(
        self,
        experiment: str,
        kind: str,
        title: str,
        details: dict[str, Any],
        one_time_usd: float,
        monthly_usd: float,
        status: str = "pending",
    ) -> int:
        cur = self.conn.execute(
            """INSERT INTO approvals (experiment, kind, title, details, one_time_usd, monthly_usd, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (experiment, kind, title, json.dumps(details, sort_keys=True), one_time_usd, monthly_usd, status, now()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def decide(self, approval_id: int, status: str, note: str = "") -> dict[str, Any]:
        if status not in {"approved", "rejected", "executed"}:
            raise ValueError(f"invalid approval status: {status}")
        self.conn.execute(
            "UPDATE approvals SET status = ?, decided_at = ?, decision_note = ? WHERE id = ?",
            (status, now(), note, approval_id),
        )
        self.conn.commit()
        return self.approval(approval_id)

    def approval(self, approval_id: int) -> dict[str, Any]:
        rows = self._rows("SELECT * FROM approvals WHERE id = ?", (approval_id,))
        if not rows:
            raise KeyError(f"no approval #{approval_id}")
        return rows[0]

    def approvals(self, experiment: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM approvals WHERE 1=1", []
        if experiment:
            sql += " AND experiment = ?"
            params.append(experiment)
        if status:
            sql += " AND status = ?"
            params.append(status)
        return self._rows(sql + " ORDER BY id", tuple(params))

    def committed_external_spend(self, experiment: str | None = None) -> tuple[float, float]:
        """(one-time, monthly) USD of approved/executed spend requests."""
        sql = (
            "SELECT COALESCE(SUM(one_time_usd),0), COALESCE(SUM(monthly_usd),0) FROM approvals "
            "WHERE kind = 'spend' AND status IN ('approved','executed')"
        )
        params: tuple[Any, ...] = ()
        if experiment:
            sql += " AND experiment = ?"
            params = (experiment,)
        row = self.conn.execute(sql, params).fetchone()
        return float(row[0]), float(row[1])

    # -- learnings --------------------------------------------------------
    def add_learning(self, experiment: str, text: str) -> None:
        self.conn.execute("INSERT INTO learnings (experiment, text, ts) VALUES (?, ?, ?)", (experiment, text, now()))
        self.conn.commit()

    def learnings(self, experiment: str, limit: int = 20) -> list[dict[str, Any]]:
        rows = self._rows("SELECT * FROM learnings WHERE experiment = ? ORDER BY id DESC LIMIT ?", (experiment, limit))
        return rows[::-1]  # oldest first
