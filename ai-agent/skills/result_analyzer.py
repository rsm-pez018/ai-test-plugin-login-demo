import json


def read_execution_results(execution_file):
    with open(execution_file, "r", encoding="utf-8") as file:
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
                "method": result["method"],
                "endpoint": result["endpoint"],
                "test_data": result["test_data"],
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


def save_result_analysis(analysis_result, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(analysis_result, file, indent=2)


def run(execution_file, output_file):
    execution_results = read_execution_results(execution_file)
    analysis_result = analyze_test_results(execution_results)
    save_result_analysis(analysis_result, output_file)

    return analysis_result
