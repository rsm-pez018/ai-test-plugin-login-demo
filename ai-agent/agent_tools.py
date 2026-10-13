"""Controlled tools exposed to an Agent through Function Calling."""

import json
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from evidence import redact
from run_agent import get_paths, load_target_config
from skills import test_executor
from workspace import Workspace


FUNCTION_TOOLS = [
    {
        "type": "function",
        "name": "read_project_context",
        "description": "Read the active project's PRD and target API contract.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_execution_result",
        "description": "Read the deterministic API execution results for the current run.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "execute_api_test",
        "description": "Execute one API test against the configured target. Only configured relative endpoints are allowed.",
        "parameters": {
            "type": "object",
            "properties": {
                "test_case_id": {"type": "string"},
                "scenario": {"type": "string"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                "endpoint": {"type": "string"},
                "test_data": {"type": "string", "description": "JSON object containing request data."},
                "expected_status_code": {"type": "integer"},
                "expected_message": {"type": "string"},
            },
            "required": [
                "test_case_id", "scenario", "method", "endpoint", "test_data",
                "expected_status_code", "expected_message",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_bug_report_draft",
        "description": "Create a deterministic bug report draft from failed execution evidence.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def _read_json(path: Path) -> Any:
    if not path.exists():
        return {"status": "error", "message": f"Missing artifact: {path.name}"}
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_target_url(base_url: str, endpoint: str) -> str:
    if not endpoint.startswith("/") or "://" in endpoint:
        raise ValueError("endpoint must be a relative path")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("configured base_url must be an HTTP(S) URL")
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"


def execute_tool(name: str, arguments: Dict[str, Any], workspace: Workspace) -> Dict[str, Any]:
    paths = get_paths(workspace)

    if name == "read_project_context":
        prd = workspace.prd_file.read_text(encoding="utf-8") if workspace.prd_file.exists() else ""
        return {
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
            "prd": prd[:20000],
            "target_config": _read_json(workspace.target_config_file),
        }

    if name == "get_execution_result":
        return {"execution_results": _read_json(paths["execution"])}

    if name == "execute_api_test":
        config = load_target_config(workspace)
        url = _validate_target_url(config["base_url"], arguments["endpoint"])
        test_case = dict(arguments)
        if isinstance(test_case.get("test_data"), str):
            test_case["test_data"] = json.loads(test_case["test_data"])
        if not isinstance(test_case.get("test_data"), dict):
            raise ValueError("test_data must be a JSON object")
        test_case["endpoint"] = arguments["endpoint"]
        result = test_executor.execute_test_cases([test_case], config["base_url"])[0]
        result["tool_request"] = {"url": url, "test_case_id": arguments["test_case_id"]}
        return redact(result)

    if name == "create_bug_report_draft":
        results = _read_json(paths["execution"])
        failed = [item for item in results if item.get("status") != "PASS"] if isinstance(results, list) else []
        return {
            "title": f"API test failures for {workspace.project_id}",
            "status": "DRAFT",
            "failed_count": len(failed),
            "failed_cases": redact(failed),
        }

    raise ValueError(f"Unknown tool: {name}")
