import json



def read_execution_results(execution_file):
    with open(execution_file, "r", encoding="utf-8") as file:
        return json.load(file)


def read_result_analysis(analysis_file):
    with open(analysis_file, "r", encoding="utf-8") as file:
        return json.load(file)

def read_prompt(prompt_file):
    with open(prompt_file, "r", encoding="utf-8") as file:
        return file.read()


def markdown_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate_test_report(execution_results, analysis_result, prompt_text):
    total = len(execution_results)
    passed = sum(result["status"] == "PASS" for result in execution_results)
    failed = total - passed
    passed_cases = [result for result in execution_results if result["status"] == "PASS"]
    failed_cases = [result for result in execution_results if result["status"] != "PASS"]

    lines = [
        "# Test Report",
        "",
        "## Project Name",
        "AI Testing Agent Demo - Login/Register System",
        "",
        "## Test Scope",
        "API testing of the configured target endpoints using generated requirements-based test cases.",
        "",
        "## Test Environment",
        "- Frontend: React",
        "- Backend: Flask",
        "- Database: SQLite",
        "- Testing type: API Testing",
        "",
        "## Test Summary",
        f"- Total test cases executed: {total}",
        f"- Passed test cases: {passed}",
        f"- Failed test cases: {failed}",
        "",
        "## Passed Test Cases",
    ]

    if passed_cases:
        lines.extend([
            "| Test case ID | Scenario |",
            "| --- | --- |",
            *[
                f"| {markdown_cell(result['test_case_id'])} | {markdown_cell(result['scenario'])} |"
                for result in passed_cases
            ],
        ])
    else:
        lines.append("No test cases passed.")

    lines.extend(["", "## Failed Test Cases"])
    if failed_cases:
        lines.extend([
            "| Test case ID | Scenario | Expected | Actual |",
            "| --- | --- | --- | --- |",
            *[
                f"| {markdown_cell(result['test_case_id'])} | "
                f"{markdown_cell(result['scenario'])} | "
                f"HTTP {result['expected_status_code']}: {markdown_cell(result['expected_message'])} | "
                f"HTTP {result['actual_status_code']}: {markdown_cell(result['actual_message'])} |"
                for result in failed_cases
            ],
        ])
    else:
        lines.append("No test cases failed.")

    lines.extend(["", "## Failure Analysis"])
    if failed_cases:
        for result in failed_cases:
            lines.extend([
                f"### {result['test_case_id']}",
                f"The scenario **{result['scenario']}** failed because the actual response "
                f"was HTTP {result['actual_status_code']} with message "
                f"`{result['actual_message']}`, while the expected response was HTTP "
                f"{result['expected_status_code']} with message "
                f"`{result['expected_message']}`.",
                "",
                "Test data:",
                "```json",
                json.dumps(result["test_data"], ensure_ascii=False, indent=2),
                "```",
                "",
            ])
    else:
        lines.append("All executed scenarios matched their expected results.")

    lines.extend([
        "## Bug Summary",
        "",
        "| Bug ID | Test case ID | Severity | Priority |",
        "| --- | --- | --- | --- |",
    ])
    if failed_cases:
        lines.extend([
            f"| BUG-{index:03d} | {markdown_cell(result['test_case_id'])} | Major | High |"
            for index, result in enumerate(failed_cases, start=1)
        ])
    else:
        lines.append("| None | — | — | — |")

    lines.extend([
        "",
        "## Conclusion",
        f"The run completed with {passed} of {total} test cases passing and {failed} failing.",
    ])
    return "\n".join(lines) + "\n"



def save_test_report(test_report, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(test_report)


def run(execution_file, analysis_file, output_file, prompt_file):
    execution_results = read_execution_results(execution_file)
    analysis_result = read_result_analysis(analysis_file)
    prompt_text = read_prompt(prompt_file)

    test_report = generate_test_report(
        execution_results,
        analysis_result,
        prompt_text
    )

    save_test_report(test_report, output_file)

    return test_report
