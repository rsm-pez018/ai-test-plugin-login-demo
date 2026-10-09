from pathlib import Path
import json

from skills import requirement_analyzer
from skills import test_case_generator
from skills import test_executor
from skills import result_analyzer
from skills import bug_report_generator
from skills import test_report_generator
from skills import test_case_validator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENT_FILE = PROJECT_ROOT / "docs" / "PRD.md"
REQUIREMENT_ANALYZER_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "requirement_analyzer_prompt.md"
TEST_CASE_GENERATOR_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "test_case_generator_prompt.md"
TEST_REPORT_GENERATOR_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "test_report_generator_prompt.md"
BUG_REPORT_GENERATOR_PROMPT_FILE = PROJECT_ROOT / "ai-agent" / "prompts" / "bug_report_generator_prompt.md"
OUTPUT_DIR = PROJECT_ROOT / "ai-agent" / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "requirements_ai.json"
TEST_CASES_OUTPUT_FILE = OUTPUT_DIR / "test_cases_ai.json"
TEST_EXECUTION_OUTPUT_FILE = OUTPUT_DIR / "test_execution_ai.json"
RESULT_ANALYSIS_OUTPUT_FILE = OUTPUT_DIR / "result_analysis_ai.json"
BUG_REPORT_OUTPUT_FILE = OUTPUT_DIR / "bug_report_ai.md"
TEST_REPORT_OUTPUT_FILE = OUTPUT_DIR / "test_report_ai.md"
TARGET_API_CONFIG_FILE = PROJECT_ROOT / "ai-agent" / "config" / "target_api.json"



def load_target_config():
    with open(
        TARGET_API_CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

def analyze_requirements():
    return requirement_analyzer.run(
        REQUIREMENT_FILE,
        OUTPUT_FILE,
        REQUIREMENT_ANALYZER_PROMPT_FILE
    )

def generate_test_cases(requirements, target_config):
    test_cases = test_case_generator.run(
        requirements,
        TEST_CASES_OUTPUT_FILE,
        TEST_CASE_GENERATOR_PROMPT_FILE,
        TARGET_API_CONFIG_FILE
    )

    return test_case_validator.run(
        test_cases,
        target_config
    )

def execute_tests(target_config):
    return test_executor.run(
        TEST_CASES_OUTPUT_FILE,
        TEST_EXECUTION_OUTPUT_FILE,
        target_config["base_url"]
    )

def generate_reports():
    analysis = result_analyzer.run(
        TEST_EXECUTION_OUTPUT_FILE,
        RESULT_ANALYSIS_OUTPUT_FILE
    )

    bug_report = bug_report_generator.run(
        RESULT_ANALYSIS_OUTPUT_FILE,
        BUG_REPORT_OUTPUT_FILE,
        BUG_REPORT_GENERATOR_PROMPT_FILE
    )

    test_report = test_report_generator.run(
        TEST_EXECUTION_OUTPUT_FILE,
        RESULT_ANALYSIS_OUTPUT_FILE,
        TEST_REPORT_OUTPUT_FILE,
        TEST_REPORT_GENERATOR_PROMPT_FILE
    )

    return analysis, bug_report, test_report

def run_all():
    target_config = load_target_config()
    requirements = analyze_requirements()

    test_cases = generate_test_cases(
        requirements,
        target_config
    )

    execution_results = execute_tests(target_config)

    analysis, bug_report, test_report = generate_reports()

    return {
        "requirements": requirements,
        "test_cases": test_cases,
        "execution_results": execution_results,
        "analysis": analysis,
        "bug_report": bug_report,
        "test_report": test_report
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
