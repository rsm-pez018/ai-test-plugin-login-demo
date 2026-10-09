import json
import requests


def read_test_cases(test_cases_file):
    with open(test_cases_file, "r", encoding="utf-8") as file:
        return json.load(file)

def send_request(api_base_url, test_case):
    method = test_case["method"].upper()
    endpoint = test_case["endpoint"]
    test_data = test_case["test_data"]

    url = (
        f"{api_base_url.rstrip('/')}/"
        f"{endpoint.lstrip('/')}"
    )

    request_options = {
        "method": method,
        "url": url,
        "timeout": 10
    }

    if method == "GET":
        request_options["params"] = test_data
    else:
        request_options["json"] = test_data

    return requests.request(**request_options)


def execute_test_cases(test_cases, api_base_url):
    execution_results = []

    for test_case in test_cases:
        try:
            response = send_request(
                api_base_url,
                test_case
            )

            try:
                response_data = response.json()
            except ValueError:
                response_data = {}

            actual_status_code = response.status_code
            actual_message = response_data.get(
                "message",
                response.text
            )

            if (
                actual_status_code
                == test_case["expected_status_code"]
                and actual_message
                == test_case["expected_message"]
            ):
                status = "PASS"
            else:
                status = "FAIL"

        except requests.RequestException as error:
            actual_status_code = None
            actual_message = str(error)
            status = "ERROR"

        execution_results.append({
            "test_case_id": test_case["test_case_id"],
            "scenario": test_case["scenario"],
            "method": test_case["method"],
            "endpoint": test_case["endpoint"],
            "test_data": test_case["test_data"],
            "expected_status_code": (
                test_case["expected_status_code"]
            ),
            "expected_message": (
                test_case["expected_message"]
            ),
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
