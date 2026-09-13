import json


def read_execution_results(execution_file):
    with open(execution_file, "r", encoding="utf-8") as file:
        return json.load(file)


def read_result_analysis(analysis_file):
    with open(analysis_file, "r", encoding="utf-8") as file:
        return json.load(file)


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


def save_test_report(test_report, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(test_report)


def run(execution_file, analysis_file, output_file):
    execution_results = read_execution_results(execution_file)
    analysis_result = read_result_analysis(analysis_file)
    test_report = generate_test_report(execution_results, analysis_result)
    save_test_report(test_report, output_file)

    return test_report