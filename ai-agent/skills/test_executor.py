import json
import requests
import time

from evidence import build_api_evidence, save_evidence


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
    return execute_test_cases_with_evidence(test_cases, api_base_url)


def execute_test_cases_with_evidence(test_cases, api_base_url, evidence_dir=None):
    execution_results = []

    for test_case in test_cases:
        started = time.perf_counter()
        request_data = {
            "method": test_case["method"].upper(),
            "endpoint": test_case["endpoint"],
            "test_data": test_case["test_data"],
        }
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
            actual_message = (
                response_data.get("message", response.text)
                if isinstance(response_data, dict)
                else response.text
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

            response_data_for_evidence = {
                "status_code": actual_status_code,
                "message": actual_message,
                "body": response_data,
                "headers": {
                    key: value
                    for key, value in response.headers.items()
                    if key.lower() in {"content-type", "location"}
                },
            }

        except requests.RequestException as error:
            actual_status_code = None
            actual_message = str(error)
            status = "ERROR"
            response_data_for_evidence = {"error": str(error)}

        duration_ms = int((time.perf_counter() - started) * 1000)
        assertions = [
            {
                "name": "status_code",
                "expected": test_case["expected_status_code"],
                "actual": actual_status_code,
                "status": "PASS" if actual_status_code == test_case["expected_status_code"] else "FAIL",
            },
            {
                "name": "message",
                "expected": test_case["expected_message"],
                "actual": actual_message,
                "status": "PASS" if actual_message == test_case["expected_message"] else "FAIL",
            },
        ]
        evidence = build_api_evidence(
            request_data,
            response_data_for_evidence,
            assertions,
            duration_ms,
        )

        result = {
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
            "status": status,
            "duration_ms": duration_ms,
            "evidence": evidence,
        }
        if evidence_dir is not None:
            result["evidence_file"] = save_evidence(
                evidence,
                evidence_dir,
                test_case["test_case_id"],
            )
        execution_results.append(result)

    return execution_results

def save_execution_results(execution_results, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(execution_results, file, indent=2)


def run(test_cases_file, output_file, api_base_url, evidence_dir=None):
    test_cases = read_test_cases(test_cases_file)
    execution_results = execute_test_cases_with_evidence(
        test_cases,
        api_base_url,
        evidence_dir,
    )
    save_execution_results(execution_results, output_file)

    return execution_results
