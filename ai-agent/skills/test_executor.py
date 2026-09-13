import json
import requests


def read_test_cases(test_cases_file):
    with open(test_cases_file, "r", encoding="utf-8") as file:
        return json.load(file)


def execute_test_cases(test_cases, api_base_url):
    execution_results = []

    for test_case in test_cases:
        url = api_base_url + test_case["endpoint"]

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


def save_execution_results(execution_results, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(execution_results, file, indent=2)


def run(test_cases_file, output_file, api_base_url):
    test_cases = read_test_cases(test_cases_file)
    execution_results = execute_test_cases(test_cases, api_base_url)
    save_execution_results(execution_results, output_file)

    return execution_results