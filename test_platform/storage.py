import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from common.tools import get_project_path

DB_PATH = os.path.join(get_project_path(), "report", "platform.db")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_runs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                target TEXT NOT NULL,
                markers TEXT,
                keyword TEXT,
                total INTEGER DEFAULT 0,
                passed INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                broken INTEGER DEFAULT 0,
                skipped INTEGER DEFAULT 0,
                exit_code INTEGER,
                error_message TEXT,
                created_at TEXT NOT NULL,
                finished_at TEXT,
                report_path TEXT
            )
            """
        )


def create_run(
    target: str = "testcases",
    markers: Optional[str] = None,
    keyword: Optional[str] = None,
) -> str:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO test_runs
            (id, status, target, markers, keyword, created_at, report_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                "pending",
                target,
                markers,
                keyword,
                now_str(),
                f"report/history/{run_id}/html",
            ),
        )
    return run_id


def update_run(run_id: str, **fields):
    if not fields:
        return
    columns = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [run_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE test_runs SET {columns} WHERE id = ?", values)


def get_run(run_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM test_runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else None


def list_runs(limit: int = 50) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM test_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_stats() -> dict:
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM test_runs").fetchone()[0]
        success = conn.execute(
            "SELECT COUNT(*) FROM test_runs WHERE status = 'success'"
        ).fetchone()[0]
        failed = conn.execute(
            "SELECT COUNT(*) FROM test_runs WHERE status IN ('failed', 'error')"
        ).fetchone()[0]
        running = conn.execute(
            "SELECT COUNT(*) FROM test_runs WHERE status IN ('pending', 'running')"
        ).fetchone()[0]
    return {
        "total_runs": total,
        "success_runs": success,
        "failed_runs": failed,
        "running_runs": running,
    }
