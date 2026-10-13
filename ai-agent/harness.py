"""Deterministic workflow runtime for the AI Testing Agent."""

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable, Dict, Optional

from workspace import Workspace


class WorkflowRunner:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.trace_file = workspace.run_dir / "trace.jsonl"
        self.metadata_file = workspace.metadata_file

    def _event(self, event_type: str, **payload: Any) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "project_id": self.workspace.project_id,
            "run_id": self.workspace.run_id,
            **payload,
        }
        with self.trace_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, default=str) + "\n")

    def set_status(self, status: str, **extra: Any) -> None:
        metadata = {}
        if self.metadata_file.exists():
            try:
                metadata = json.loads(self.metadata_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                metadata = {}
        metadata.update({"status": status, **extra})
        self.metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self._event("run.status", status=status, **extra)

    def run_stage(
        self,
        name: str,
        operation: Callable[[], Any],
        retries: int = 0,
    ) -> Any:
        attempts = 0
        while True:
            attempts += 1
            started = time.perf_counter()
            self._event("stage.started", stage=name, attempt=attempts)
            try:
                result = operation()
                duration_ms = int((time.perf_counter() - started) * 1000)
                self._event(
                    "stage.succeeded",
                    stage=name,
                    attempt=attempts,
                    duration_ms=duration_ms,
                )
                return result
            except Exception as error:
                duration_ms = int((time.perf_counter() - started) * 1000)
                self._event(
                    "stage.failed",
                    stage=name,
                    attempt=attempts,
                    duration_ms=duration_ms,
                    error=str(error),
                )
                if attempts > retries:
                    raise

    def finish(self, status: str = "COMPLETED", **extra: Any) -> None:
        self.set_status(status, finished_at=datetime.now(timezone.utc).isoformat(), **extra)
