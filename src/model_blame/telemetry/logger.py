from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from model_blame.simir.models import TelemetryBatch, TelemetrySample


class TelemetryLogger:
    def __init__(self, jsonl_path: str | Path | None = None, sqlite_path: str | Path | None = None):
        self.jsonl_path = Path(jsonl_path) if jsonl_path else None
        self.sqlite_path = Path(sqlite_path) if sqlite_path else None
        if self.jsonl_path:
            self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        if self.sqlite_path:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_sqlite()

    def log_batch(self, batch: TelemetryBatch) -> None:
        if self.jsonl_path:
            with self.jsonl_path.open("a", encoding="utf-8") as handle:
                for sample in batch.samples:
                    handle.write(json.dumps(sample.model_dump(mode="json"), sort_keys=True) + "\n")
        if self.sqlite_path:
            with sqlite3.connect(self.sqlite_path) as conn:
                conn.executemany(
                    """
                    insert into telemetry (
                        timestamp, sim_time, run_id, backend, asset_id, tag, kind,
                        value_json, quality, unit, metadata_json
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [self._sqlite_row(sample) for sample in batch.samples],
                )

    def _init_sqlite(self) -> None:
        assert self.sqlite_path is not None
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                create table if not exists telemetry (
                    id integer primary key autoincrement,
                    timestamp text not null,
                    sim_time real,
                    run_id text not null,
                    backend text not null,
                    asset_id text not null,
                    tag text not null,
                    kind text not null,
                    value_json text,
                    quality text not null,
                    unit text,
                    metadata_json text not null
                )
                """
            )
            conn.execute("create index if not exists idx_telemetry_run on telemetry(run_id)")
            conn.execute("create index if not exists idx_telemetry_tag on telemetry(asset_id, tag)")

    def _sqlite_row(self, sample: TelemetrySample) -> tuple[object, ...]:
        data = sample.model_dump(mode="json")
        return (
            data["timestamp"],
            data["sim_time"],
            data["run_id"],
            data["backend"],
            data["asset_id"],
            data["tag"],
            data["kind"],
            json.dumps(data["value"], sort_keys=True),
            data["quality"],
            data["unit"],
            json.dumps(data["metadata"], sort_keys=True),
        )
