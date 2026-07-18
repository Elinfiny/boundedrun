from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from app.models import RunReceipt

DB_PATH = Path("boundedrun.db")


def initialize() -> None:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                receipt_json TEXT NOT NULL
            )
            """
        )


def save_receipt(receipt: RunReceipt) -> None:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO runs(run_id, created_at, receipt_json) VALUES (?, ?, ?)",
            (
                receipt.run_id,
                receipt.created_at.isoformat(),
                receipt.model_dump_json(),
            ),
        )
        connection.commit()


def get_receipt(run_id: str) -> RunReceipt | None:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute(
            "SELECT receipt_json FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
    if not row:
        return None
    return RunReceipt.model_validate(json.loads(row[0]))


def list_receipts(limit: int = 20) -> list[RunReceipt]:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        rows = connection.execute(
            "SELECT receipt_json FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [RunReceipt.model_validate(json.loads(row[0])) for row in rows]
