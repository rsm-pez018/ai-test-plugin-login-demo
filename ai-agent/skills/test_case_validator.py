REQUIRED_FIELDS = {
    "test_case_id",
    "related_requirement_id",
    "scenario",
    "method",
    "endpoint",
    "test_data",
    "expected_status_code",
    "expected_message",
    "priority"
}


def validate_test_cases(test_cases, api_config):
    errors = []

    if not isinstance(test_cases, list):
        raise ValueError("Test cases must be a JSON array.")

    if len(test_cases) == 0:
        raise ValueError("No test cases were generated.")

    configured_endpoints = {
        (
            endpoint["method"].upper(),
            endpoint["path"]
        )
        for endpoint in api_config["endpoints"]
    }

    request_fields_by_endpoint = {
        endpoint["path"]: set(
            endpoint.get("request_body", {}).keys()
        )
        for endpoint in api_config["endpoints"]
    }

    test_case_ids = set()
    positive_endpoints = set()

    for index, test_case in enumerate(test_cases, start=1):
        label = f"Test case #{index}"

        if not isinstance(test_case, dict):
            errors.append(f"{label} must be a JSON object.")
            continue

        missing_fields = REQUIRED_FIELDS - set(test_case.keys())

        if missing_fields:
            errors.append(
                f"{label} is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )
            continue

        test_case_id = test_case["test_case_id"]

        if test_case_id in test_case_ids:
            errors.append(
                f"Duplicate test_case_id: {test_case_id}"
            )
        else:
            test_case_ids.add(test_case_id)

        method = str(test_case["method"]).upper()
        endpoint = test_case["endpoint"]

        if (method, endpoint) not in configured_endpoints:
            errors.append(
                f"{test_case_id} uses an unconfigured API: "
                f"{method} {endpoint}"
            )

        if not isinstance(test_case["test_data"], dict):
            errors.append(
                f"{test_case_id} test_data must be a JSON object."
            )
        else:
            configured_fields = request_fields_by_endpoint.get(
                endpoint,
                set()
            )
            generated_fields = set(test_case["test_data"].keys())
            unknown_fields = generated_fields - configured_fields

            if unknown_fields:
                errors.append(
                    f"{test_case_id} contains unknown request fields: "
                    f"{', '.join(sorted(unknown_fields))}"
                )

        if not isinstance(test_case["expected_status_code"], int):
            errors.append(
                f"{test_case_id} expected_status_code must be an integer."
            )
        elif 200 <= test_case["expected_status_code"] < 300:
            positive_endpoints.add((method, endpoint))

        if not isinstance(test_case["expected_message"], str):
            errors.append(
                f"{test_case_id} expected_message must be a string."
            )

    for endpoint_config in api_config["endpoints"]:
        endpoint_key = (
            endpoint_config["method"].upper(),
            endpoint_config["path"]
        )
        has_success_response = any(
            200 <= response.get("status_code", 0) < 300
            for response in endpoint_config.get("expected_responses", [])
        )

        if has_success_response and endpoint_key not in positive_endpoints:
            method, endpoint = endpoint_key
            errors.append(
                f"Missing positive test case for configured API: "
                f"{method} {endpoint}"
            )

    if errors:
        error_message = "\n".join(
            f"- {error}" for error in errors
        )

        raise ValueError(
            "Test case validation failed:\n"
            f"{error_message}"
        )

    return test_cases


def run(test_cases, api_config):
    return validate_test_cases(test_cases, api_config)
