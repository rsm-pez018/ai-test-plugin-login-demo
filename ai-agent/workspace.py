"""Project and run workspace management for the AI Testing Agent."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import uuid
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACES_DIR = PROJECT_ROOT / "ai-agent" / "workspaces"
ACTIVE_STATE_FILE = WORKSPACES_DIR / ".active.json"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "project").strip())
    return value.strip("-").lower() or "project"


@dataclass(frozen=True)
class Workspace:
    project_id: str
    run_id: str
    project_dir: Path
    run_dir: Path
    prd_file: Path
    target_config_file: Path
    output_dir: Path

    @property
    def metadata_file(self) -> Path:
        return self.run_dir / "run.json"

    def ensure(self) -> "Workspace":
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / "evidence").mkdir(exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self


def _write_active_state(project_id: str, run_id: Optional[str] = None) -> None:
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_STATE_FILE.write_text(
        json.dumps(
            {
                "project_id": project_id,
                "run_id": run_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _read_active_state() -> dict:
    if not ACTIVE_STATE_FILE.exists():
        return {}
    try:
        return json.loads(ACTIVE_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def project_id_for_name(project_name: str) -> str:
    return slugify(project_name)


def activate_project(project_name: str) -> str:
    project_id = project_id_for_name(project_name)
    project_dir = WORKSPACES_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    _write_active_state(project_id)
    return project_id


def get_active_project_id() -> str:
    project_id = _read_active_state().get("project_id")
    if project_id:
        return project_id
    return activate_project("default-project")


def activate_run(project_id: Optional[str] = None, run_id: Optional[str] = None) -> Workspace:
    project_id = project_id or get_active_project_id()
    project_dir = WORKSPACES_DIR / slugify(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    if not run_id:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"run-{timestamp}-{uuid.uuid4().hex[:8]}"

    run_dir = project_dir / "runs" / run_id
    workspace = Workspace(
        project_id=slugify(project_id),
        run_id=run_id,
        project_dir=project_dir,
        run_dir=run_dir,
        prd_file=project_dir / "prd.md",
        target_config_file=project_dir / "target_api.json",
        output_dir=run_dir / "outputs",
    ).ensure()

    if not workspace.metadata_file.exists():
        workspace.metadata_file.write_text(
            json.dumps(
                {
                    "project_id": workspace.project_id,
                    "run_id": workspace.run_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "status": "CREATED",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    _write_active_state(workspace.project_id, workspace.run_id)
    return workspace


def get_active_workspace(create_run: bool = True) -> Workspace:
    state = _read_active_state()
    project_id = state.get("project_id") or get_active_project_id()
    run_id = state.get("run_id")
    if create_run and not run_id:
        return activate_run(project_id)
    return activate_run(project_id, run_id)


def save_project_prd(project_id: str, text: str) -> Path:
    project_dir = WORKSPACES_DIR / slugify(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    path = project_dir / "prd.md"
    path.write_text(text, encoding="utf-8")
    return path


def save_target_config(project_id: str, config: dict) -> Path:
    project_dir = WORKSPACES_DIR / slugify(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    path = project_dir / "target_api.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return path


def snapshot_inputs(workspace: Workspace) -> None:
    inputs_dir = workspace.run_dir / "inputs"
    inputs_dir.mkdir(exist_ok=True)
    for source in (workspace.prd_file, workspace.target_config_file):
        if source.exists():
            shutil.copy2(source, inputs_dir / source.name)
