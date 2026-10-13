"""Run the AI Agent against controlled defect variants.

This script measures Agent detection. It does not fill in the manual baseline;
that must be measured by a person using manual_baseline.md.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import requests

AI_AGENT_DIR = Path(__file__).resolve().parents[1] / "ai-agent"
PROJECT_ROOT = AI_AGENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
sys.path.insert(0, str(AI_AGENT_DIR))

from run_agent import run_all  # noqa: E402
from workspace import activate_run, save_project_prd, save_target_config  # noqa: E402


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def start_backend(port, mutation, database_path):
    python = BACKEND_DIR / "venv" / "bin" / "python"
    if not python.exists():
        python = Path(sys.executable)
    environment = os.environ.copy()
    environment.update({
        "AI_TEST_MUTATIONS": mutation,
        "AI_TEST_DB": str(database_path),
        "FLASK_DEBUG": "0",
        "PORT": str(port),
        "PYTHONUNBUFFERED": "1",
    })
    process = subprocess.Popen(
        [str(python), "app.py"],
        cwd=str(BACKEND_DIR),
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            response = requests.post(
                f"http://127.0.0.1:{port}/api/login",
                json={},
                timeout=1,
            )
            if response.status_code == 400:
                return process
        except requests.RequestException:
            time.sleep(0.2)
    process.terminate()
    raise RuntimeError(f"Backend did not start on port {port}")


def stop_backend(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def detected_bug(execution_results, bug):
    keywords = [item.lower() for item in bug["scenario_keywords"]]
    for result in execution_results:
        if result.get("status") not in {"FAIL", "ERROR"}:
            continue
        scenario = result.get("scenario", "").lower()
        if any(keyword in scenario for keyword in keywords):
            return True
    return False


def run_one(bug, run_number, prd_text, target_template, port):
    project_name = f"evaluation-{bug['bug_id'].lower()}-{run_number}"
    project_id = project_name
    workspace = activate_run(project_id)
    save_project_prd(project_id, prd_text)
    target = dict(target_template)
    target["project_name"] = project_name
    target["base_url"] = f"http://127.0.0.1:{port}"
    save_target_config(project_id, target)

    with tempfile.TemporaryDirectory(prefix=f"ai-qa-{bug['bug_id']}-") as temp_dir:
        process = start_backend(port, bug["mutation"], Path(temp_dir) / "users.db")
        started = time.perf_counter()
        try:
            result = run_all(workspace)
        finally:
            stop_backend(process)
        duration_seconds = round(time.perf_counter() - started, 2)

    return {
        "bug_id": bug["bug_id"],
        "run_number": run_number,
        "project_id": project_id,
        "run_id": result["run_id"],
        "duration_seconds": duration_seconds,
        "detected": detected_bug(result["execution_results"], bug),
        "failed_cases": [
            item.get("test_case_id")
            for item in result["execution_results"]
            if item.get("status") in {"FAIL", "ERROR"}
        ],
        "workspace": result["workspace"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--only", nargs="*", help="Only evaluate selected bug IDs, e.g. B1 B2")
    args = parser.parse_args()

    bugs = load_json(EVALUATION_DIR / "known_bugs.json")
    if args.only:
        bugs = [bug for bug in bugs if bug["bug_id"] in args.only]
    prd_text = (EVALUATION_DIR / "evaluation_prd.md").read_text(encoding="utf-8")
    target_template = load_json(EVALUATION_DIR / "evaluation_target_api.json")
    records = []

    for index, bug in enumerate(bugs):
        for run_number in range(1, args.runs + 1):
            port = 5100 + index * 10 + run_number
            print(f"Running {bug['bug_id']} ({run_number}/{args.runs})...", flush=True)
            records.append(run_one(bug, run_number, prd_text, target_template, port))

    detected = sum(1 for record in records if record["detected"])
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runs": args.runs,
        "known_bug_count": len(bugs),
        "total_trials": len(records),
        "detected_trials": detected,
        "trial_recall": round(detected / len(records), 4) if records else 0,
        "records": records,
    }
    output_dir = EVALUATION_DIR / "results"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "agent_runs.json"
    output_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
