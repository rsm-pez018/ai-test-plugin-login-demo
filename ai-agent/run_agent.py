from pathlib import Path

from skills import requirement_analyzer
from skills import test_case_generator
from skills import test_executor
from skills import result_analyzer
from skills import bug_report_generator
from skills import test_report_generator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENT_FILE = PROJECT_ROOT / "docs" / "register_requirement.md"
OUTPUT_DIR = PROJECT_ROOT / "ai-agent" / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "requirements_ai.json"
TEST_CASES_OUTPUT_FILE = OUTPUT_DIR / "test_cases_ai.json"
TEST_EXECUTION_OUTPUT_FILE = OUTPUT_DIR / "test_execution_ai.json"
RESULT_ANALYSIS_OUTPUT_FILE = OUTPUT_DIR / "result_analysis_ai.json"
BUG_REPORT_OUTPUT_FILE = OUTPUT_DIR / "bug_report_ai.md"
TEST_REPORT_OUTPUT_FILE = OUTPUT_DIR / "test_report_ai.md"


API_BASE_URL = "http://127.0.0.1:5000"


def main():
    requirements = requirement_analyzer.run(
        REQUIREMENT_FILE,
        OUTPUT_FILE
    )

    test_cases = test_case_generator.run(
        requirements,
        TEST_CASES_OUTPUT_FILE
    )

    execution_results = test_executor.run(
        TEST_CASES_OUTPUT_FILE,
        TEST_EXECUTION_OUTPUT_FILE,
        API_BASE_URL
    )

    analysis_result = result_analyzer.run(
        TEST_EXECUTION_OUTPUT_FILE,
        RESULT_ANALYSIS_OUTPUT_FILE
    )

    bug_report = bug_report_generator.run(
        RESULT_ANALYSIS_OUTPUT_FILE,
        BUG_REPORT_OUTPUT_FILE
    )

    test_report = test_report_generator.run(
        TEST_EXECUTION_OUTPUT_FILE,
        RESULT_ANALYSIS_OUTPUT_FILE,
        TEST_REPORT_OUTPUT_FILE
    )

    print("Requirement Analyzer finished.")
    print(f"Generated {len(requirements)} requirements.")
    print(f"Output file: {OUTPUT_FILE}")
    print("Test Case Generator finished.")
    print(f"Generated {len(test_cases)} test cases.")
    print(f"Output file: {TEST_CASES_OUTPUT_FILE}")
    print("Test Executor finished.")
    print(f"Executed {len(execution_results)} test cases.")
    print(f"Output file: {TEST_EXECUTION_OUTPUT_FILE}")
    print("Result Analyzer finished.")
    print(f"Passed: {analysis_result['passed']}")
    print(f"Failed: {analysis_result['failed']}")
    print(f"Output file: {RESULT_ANALYSIS_OUTPUT_FILE}")
    print("Bug Report Generator finished.")
    print(f"Output file: {BUG_REPORT_OUTPUT_FILE}")
    print("Test Report Generator finished.")
    print(f"Output file: {TEST_REPORT_OUTPUT_FILE}")

if __name__ == "__main__":
    main()
