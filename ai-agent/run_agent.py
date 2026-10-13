from pathlib import Path
import json
from datetime import datetime, timezone

from skills import requirement_analyzer
from skills import test_case_generator
from skills import test_executor
from skills import result_analyzer
from skills import bug_report_generator
from skills import test_report_generator
from skills import test_case_validator
from harness import WorkflowRunner
from workspace import Workspace, get_active_workspace, snapshot_inputs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENT_ANALYZER_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "requirement_analyzer_prompt.md"
TEST_CASE_GENERATOR_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "test_case_generator_prompt.md"
TEST_REPORT_GENERATOR_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "test_report_generator_prompt.md"
BUG_REPORT_GENERATOR_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "bug_report_generator_prompt.md"
def get_paths(workspace: Workspace) -> dict:
    output_dir = workspace.output_dir
    return {
        "requirement_file": workspace.prd_file,
        "target_config_file": workspace.target_config_file,
        "output_dir": output_dir,
        "requirements": output_dir / "requirements_ai.json",
        "test_cases": output_dir / "test_cases_ai.json",
        "execution": output_dir / "test_execution_ai.json",
        "analysis": output_dir / "result_analysis_ai.json",
        "bug_report": output_dir / "bug_report_ai.md",
        "test_report": output_dir / "test_report_ai.md",
    }



def load_target_config(workspace=None):
    workspace = workspace or get_active_workspace()
    paths = get_paths(workspace)
    with open(
        paths["target_config_file"],
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

def analyze_requirements(workspace=None):
    workspace = workspace or get_active_workspace()
    paths = get_paths(workspace)
    return requirement_analyzer.run(
        paths["requirement_file"],
        paths["requirements"],
        REQUIREMENT_ANALYZER_PROMPT_FILE
    )

def generate_test_cases(requirements, target_config, workspace=None):
    workspace = workspace or get_active_workspace()
    paths = get_paths(workspace)
    test_cases = test_case_generator.run(
        requirements,
        paths["test_cases"],
        TEST_CASE_GENERATOR_PROMPT_FILE,
        paths["target_config_file"]
    )

    validated = test_case_validator.run(
        test_cases,
        target_config
    )
    paths["test_cases"].write_text(
        json.dumps(validated, indent=2),
        encoding="utf-8",
    )
    return validated

def execute_tests(target_config, workspace=None):
    workspace = workspace or get_active_workspace()
    paths = get_paths(workspace)
    return test_executor.run(
        paths["test_cases"],
        paths["execution"],
        target_config["base_url"],
        workspace.run_dir / "evidence",
    )

def generate_reports(workspace=None):
    workspace = workspace or get_active_workspace()
    paths = get_paths(workspace)
    analysis = result_analyzer.run(
        paths["execution"],
        paths["analysis"]
    )

    bug_report = bug_report_generator.run(
        paths["analysis"],
        paths["bug_report"],
        BUG_REPORT_GENERATOR_PROMPT_FILE
    )

    test_report = test_report_generator.run(
        paths["execution"],
        paths["analysis"],
        paths["test_report"],
        TEST_REPORT_GENERATOR_PROMPT_FILE
    )

    return analysis, bug_report, test_report

def run_all(workspace=None):
    workspace = workspace or get_active_workspace()
    runner = WorkflowRunner(workspace)
    runner.set_status("RUNNING", started_at=datetime.now(timezone.utc).isoformat())
    try:
        snapshot_inputs(workspace)
        target_config = runner.run_stage(
            "load_target_config",
            lambda: load_target_config(workspace),
        )
        requirements = runner.run_stage(
            "analyze_requirements",
            lambda: analyze_requirements(workspace),
        )
        test_cases = runner.run_stage(
            "generate_and_validate_test_cases",
            lambda: generate_test_cases(requirements, target_config, workspace),
        )
        execution_results = runner.run_stage(
            "execute_tests",
            lambda: execute_tests(target_config, workspace),
        )
        analysis, bug_report, test_report = runner.run_stage(
            "generate_reports",
            lambda: generate_reports(workspace),
        )
        runner.finish("COMPLETED")
    except Exception as error:
        runner.finish("FAILED", error=str(error))
        raise

    return {
        "requirements": requirements,
        "test_cases": test_cases,
        "execution_results": execution_results,
        "analysis": analysis,
        "bug_report": bug_report,
        "test_report": test_report,
        "project_id": workspace.project_id,
        "run_id": workspace.run_id,
        "workspace": str(workspace.run_dir),
        "trace": str(runner.trace_file),
    }

def main():
    result = run_all()

    print("AI Testing Agent finished.")
    print(
        f"Requirements: {len(result['requirements'])}"
    )
    print(
        f"Test cases: {len(result['test_cases'])}"
    )
    print(
        f"Executed: {len(result['execution_results'])}"
    )
    print(f"Passed: {result['analysis']['passed']}")
    print(f"Failed: {result['analysis']['failed']}")

if __name__ == "__main__":
    main()
