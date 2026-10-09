import json


def read_result_analysis(analysis_file):
    with open(analysis_file, "r", encoding="utf-8") as file:
        return json.load(file)


def read_prompt(prompt_file):
    with open(prompt_file, "r", encoding="utf-8") as file:
        return file.read()


def format_test_data(test_data):
    return json.dumps(test_data, ensure_ascii=False, indent=2)


def generate_bug_report(analysis_result, prompt_text):
    failed_cases = analysis_result.get("failed_cases", [])

    if not failed_cases:
        return "# Bug Report\n\nNo bugs were found during this test run.\n"

    reports = ["# Bug Report", ""]

    for index, case in enumerate(failed_cases, start=1):
        reports.extend([
            f"## Bug ID: BUG-{index:03d}",
            f"**Title:** {case['scenario']}",
            f"**Related test case ID:** {case['test_case_id']}",
            f"**Module or endpoint:** {case['method']} {case['endpoint']}",
            "**Preconditions:** The target API is available.",
            "**Steps to reproduce:**",
            f"1. Send a `{case['method']} {case['endpoint']}` request.",
            "2. Compare the response with the expected result.",
            "**Test data:**",
            "```json",
            format_test_data(case["test_data"]),
            "```",
            "**Expected result:**",
            f"- HTTP {case['expected_status_code']}",
            f"- Message: `{case['expected_message']}`",
            "**Actual result:**",
            f"- HTTP {case['actual_status_code']}",
            f"- Message: `{case['actual_message']}`",
            f"**Failure reason:** {case['failure_reason']}",
            "**Severity:** Major",
            "**Priority:** High",
            "**Status:** Open",
            "",
        ])

    return "\n".join(reports)


def save_bug_report(bug_report, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(bug_report)


def run(analysis_file, output_file, prompt_file):
    analysis_result = read_result_analysis(analysis_file)
    prompt_text = read_prompt(prompt_file)

    bug_report = generate_bug_report(
        analysis_result,
        prompt_text
    )

    save_bug_report(bug_report, output_file)

    return bug_report
