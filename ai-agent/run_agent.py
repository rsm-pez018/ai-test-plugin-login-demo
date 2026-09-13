import json
from pathlib import Path
import requests
import uuid


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


def read_requirement_file():
    with open(REQUIREMENT_FILE, "r", encoding="utf-8") as file:
        return file.read()


def analyze_requirements(requirement_text):
    text = requirement_text.lower()
    requirements = []

    if "username" in text:
        requirements.append({
            "requirement_id": "REQ_REGISTER_001",
            "module": "Register",
            "field": "username",
            "rule": "Username is required",
            "expected_behavior": "Registration should fail when username is empty"
        })

        requirements.append({
            "requirement_id": "REQ_REGISTER_002",
            "module": "Register",
            "field": "username",
            "rule": "Username length must be greater than or equal to 6 characters",
            "expected_behavior": "Registration should fail when username length is less than 6 characters"
        })

    if "password" in text:
        requirements.append({
            "requirement_id": "REQ_REGISTER_003",
            "module": "Register",
            "field": "password",
            "rule": "Password is required",
            "expected_behavior": "Registration should fail when password is empty"
        })

        requirements.append({
            "requirement_id": "REQ_REGISTER_004",
            "module": "Register",
            "field": "password",
            "rule": "Password length must be greater than or equal to 6 characters",
            "expected_behavior": "Registration should fail when password length is less than 6 characters"
        })

    return requirements


def save_requirements(requirements):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(requirements, file, indent=2)


def generate_test_cases(requirements):
    test_cases = []
    run_id = uuid.uuid4().hex[:8]
    valid_username = f"user{run_id}"
    short_username = f"u{run_id[:4]}"
    password_test_username = f"pass{run_id}"

    requirement_ids = {
        requirement["requirement_id"]
        for requirement in requirements
    }

    if "REQ_REGISTER_001" in requirement_ids:
        test_cases.append({
            "test_case_id": "TC_REGISTER_001",
            "related_requirement_id": "REQ_REGISTER_001",
            "scenario": "Register with valid username and password",
            "method": "POST",
            "endpoint": "/api/register",
            "test_data": {
                "username": valid_username,
                "password": "123456"
            },
            "expected_status_code": 200,
            "expected_message": "Registration_successful",
            "priority": "High"
        })

        test_cases.append({
            "test_case_id": "TC_REGISTER_002",
            "related_requirement_id": "REQ_REGISTER_001",
            "scenario": "Register with empty username",
            "method": "POST",
            "endpoint": "/api/register",
            "test_data": {
                "username": "",
                "password": "123456"
            },
            "expected_status_code": 400,
            "expected_message": "Username is required",
            "priority": "High"
        })

    if "REQ_REGISTER_002" in requirement_ids:
        test_cases.append({
            "test_case_id": "TC_REGISTER_003",
            "related_requirement_id": "REQ_REGISTER_002",
            "scenario": "Register with username length less than 6 characters",
            "method": "POST",
            "endpoint": "/api/register",
            "test_data": {
                "username": short_username,
                "password": "123456"
            },
            "expected_status_code": 400,
            "expected_message": "Username length must be at least 6 characters",
            "priority": "High"
        })

    if "REQ_REGISTER_003" in requirement_ids:
        test_cases.append({
            "test_case_id": "TC_REGISTER_004",
            "related_requirement_id": "REQ_REGISTER_003",
            "scenario": "Register with empty password",
            "method": "POST",
            "endpoint": "/api/register",
            "test_data": {
                "username": password_test_username,
                "password": ""
            },
            "expected_status_code": 400,
            "expected_message": "Password is required",
            "priority": "High"
        })

    if "REQ_REGISTER_004" in requirement_ids:
        test_cases.append({
            "test_case_id": "TC_REGISTER_005",
            "related_requirement_id": "REQ_REGISTER_004",
            "scenario": "Register with password length less than 6 characters",
            "method": "POST",
            "endpoint": "/api/register",
            "test_data": {
                "username": password_test_username,
                "password": "123"
            },
            "expected_status_code": 400,
            "expected_message": "Password length must be at least 6 characters",
            "priority": "High"
        })

    return test_cases

def save_test_cases(test_cases):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(TEST_CASES_OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(test_cases, file, indent=2)

def read_test_cases():
    with open(TEST_CASES_OUTPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    

def execute_test_cases(test_cases):
    execution_results = []

    for test_case in test_cases:
        url = API_BASE_URL + test_case["endpoint"]

        response = requests.post(
            url,
            json=test_case["test_data"]
        )

        response_data = response.json()

        actual_status_code = response.status_code
        actual_message = response_data.get("message")

        if (
            actual_status_code == test_case["expected_status_code"]
            and actual_message == test_case["expected_message"]
        ):
            status = "PASS"
        else:
            status = "FAIL"

        execution_results.append({
            "test_case_id": test_case["test_case_id"],
            "scenario": test_case["scenario"],
            "endpoint": test_case["endpoint"],
            "test_data": test_case["test_data"],
            "expected_status_code": test_case["expected_status_code"],
            "expected_message": test_case["expected_message"],
            "actual_status_code": actual_status_code,
            "actual_message": actual_message,
            "status": status
        })

    return execution_results

def save_execution_results(execution_results):
    with open(TEST_EXECUTION_OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(execution_results, file, indent=2)


def read_execution_results():
    with open(TEST_EXECUTION_OUTPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def analyze_test_results(execution_results):
    total = len(execution_results)
    passed = 0
    failed = 0
    failed_cases = []

    for result in execution_results:
        if result["status"] == "PASS":
            passed += 1
        else:
            failed += 1
            failed_cases.append({
                "test_case_id": result["test_case_id"],
                "scenario": result["scenario"],
                "expected_status_code": result["expected_status_code"],
                "expected_message": result["expected_message"],
                "actual_status_code": result["actual_status_code"],
                "actual_message": result["actual_message"],
                "failure_reason": "Actual result does not match expected result"
            })

    analysis_result = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "failed_cases": failed_cases
    }

    return analysis_result


def save_result_analysis(analysis_result):
    with open(RESULT_ANALYSIS_OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(analysis_result, file, indent=2)


def read_result_analysis():
    with open(RESULT_ANALYSIS_OUTPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    
def generate_bug_report(analysis_result):
    failed_cases = analysis_result["failed_cases"]

    if len(failed_cases) == 0:
        return "# Bug Report\n\nNo bugs found.\n"

    bug_report = "# Bug Report\n\n"

    for index, failed_case in enumerate(failed_cases, start=1):
        bug_report += f"## BUG_REGISTER_{index:03d}\n\n"
        bug_report += f"### Title\n\n"
        bug_report += f"{failed_case['scenario']} failed\n\n"
        bug_report += f"### Related Test Case\n\n"
        bug_report += f"{failed_case['test_case_id']}\n\n"
        bug_report += f"### Expected Result\n\n"
        bug_report += f"HTTP {failed_case['expected_status_code']} / {failed_case['expected_message']}\n\n"
        bug_report += f"### Actual Result\n\n"
        bug_report += f"HTTP {failed_case['actual_status_code']} / {failed_case['actual_message']}\n\n"
        bug_report += f"### Failure Reason\n\n"
        bug_report += f"{failed_case['failure_reason']}\n\n"
        bug_report += f"### Severity\n\n"
        bug_report += f"Medium\n\n"
        bug_report += f"### Status\n\n"
        bug_report += f"Open\n\n"
        bug_report += "---\n\n"

    return bug_report

def save_bug_report(bug_report):
    with open(BUG_REPORT_OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(bug_report)


def generate_test_report(execution_results, analysis_result):
    test_report = "# Test Report\n\n"

    test_report += "## Project\n\n"
    test_report += "AI Testing Agent Demo - Login/Register System\n\n"

    test_report += "## Test Environment\n\n"
    test_report += "- Frontend: React\n"
    test_report += "- Backend: Flask\n"
    test_report += "- Database: SQLite\n"
    test_report += "- Testing Type: API Testing\n\n"

    test_report += "## Test Summary\n\n"
    test_report += f"- Total Test Cases: {analysis_result['total']}\n"
    test_report += f"- Passed: {analysis_result['passed']}\n"
    test_report += f"- Failed: {analysis_result['failed']}\n\n"

    test_report += "## Test Results\n\n"

    for result in execution_results:
        test_report += f"### {result['test_case_id']}\n\n"
        test_report += f"- Scenario: {result['scenario']}\n"
        test_report += f"- Expected: HTTP {result['expected_status_code']} / {result['expected_message']}\n"
        test_report += f"- Actual: HTTP {result['actual_status_code']} / {result['actual_message']}\n"
        test_report += f"- Status: {result['status']}\n\n"

    test_report += "## Failed Test Analysis\n\n"

    if analysis_result["failed"] == 0:
        test_report += "No failed test cases.\n\n"
    else:
        for failed_case in analysis_result["failed_cases"]:
            test_report += f"### {failed_case['test_case_id']}\n\n"
            test_report += f"- Scenario: {failed_case['scenario']}\n"
            test_report += f"- Failure Reason: {failed_case['failure_reason']}\n"
            test_report += f"- Expected: HTTP {failed_case['expected_status_code']} / {failed_case['expected_message']}\n"
            test_report += f"- Actual: HTTP {failed_case['actual_status_code']} / {failed_case['actual_message']}\n\n"

    test_report += "## Bug Reference\n\n"

    if analysis_result["failed"] == 0:
        test_report += "No bug generated.\n"
    else:
        test_report += "See `bug_report_ai.md` for details.\n"

    return test_report

def save_test_report(test_report):
    with open(TEST_REPORT_OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(test_report)

def main():
    requirement_text = read_requirement_file()
    requirements = analyze_requirements(requirement_text)
    save_requirements(requirements)

    test_cases = generate_test_cases(requirements)
    save_test_cases(test_cases)

    loaded_test_cases = read_test_cases()
    execution_results = execute_test_cases(loaded_test_cases)
    save_execution_results(execution_results)

    loaded_execution_results = read_execution_results()
    analysis_result = analyze_test_results(loaded_execution_results)
    save_result_analysis(analysis_result)

    loaded_analysis_result = read_result_analysis()
    bug_report = generate_bug_report(loaded_analysis_result)
    save_bug_report(bug_report)

    test_report = generate_test_report(execution_results, analysis_result)
    save_test_report(test_report)

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
