import json


def read_result_analysis(analysis_file):
    with open(analysis_file, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_bug_report(analysis_result):
    failed_cases = analysis_result["failed_cases"]

    if len(failed_cases) == 0:
        return "# Bug Report\n\nNo bugs found.\n"

    bug_report = "# Bug Report\n\n"

    for index, failed_case in enumerate(failed_cases, start=1):
        bug_report += f"## BUG_REGISTER_{index:03d}\n\n"
        bug_report += "### Title\n\n"
        bug_report += f"{failed_case['scenario']} failed\n\n"
        bug_report += "### Related Test Case\n\n"
        bug_report += f"{failed_case['test_case_id']}\n\n"
        bug_report += "### Expected Result\n\n"
        bug_report += f"HTTP {failed_case['expected_status_code']} / {failed_case['expected_message']}\n\n"
        bug_report += "### Actual Result\n\n"
        bug_report += f"HTTP {failed_case['actual_status_code']} / {failed_case['actual_message']}\n\n"
        bug_report += "### Failure Reason\n\n"
        bug_report += f"{failed_case['failure_reason']}\n\n"
        bug_report += "### Severity\n\n"
        bug_report += "Medium\n\n"
        bug_report += "### Status\n\n"
        bug_report += "Open\n\n"
        bug_report += "---\n\n"

    return bug_report


def save_bug_report(bug_report, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(bug_report)


def run(analysis_file, output_file):
    analysis_result = read_result_analysis(analysis_file)
    bug_report = generate_bug_report(analysis_result)
    save_bug_report(bug_report, output_file)

    return bug_report