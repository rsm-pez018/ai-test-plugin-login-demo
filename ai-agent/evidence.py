"""Evidence primitives shared by executors, verifiers, and reports."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict


SENSITIVE_KEYS = {
    "password",
    "token",
    "access_token",
    "authorization",
    "api_key",
    "secret",
}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_api_evidence(
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    assertions: list,
    duration_ms: int,
) -> Dict[str, Any]:
    return {
        "type": "api",
        "captured_at": utc_now(),
        "request": redact(request_data),
        "response": redact(response_data),
        "assertions": assertions,
        "duration_ms": duration_ms,
    }


def save_evidence(evidence: Dict[str, Any], evidence_dir: Path, evidence_id: str) -> str:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{evidence_id}.json"
    path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return str(path)
