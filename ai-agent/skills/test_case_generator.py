import json
import uuid


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


def save_test_cases(test_cases, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(test_cases, file, indent=2)


def run(requirements, output_file):
    test_cases = generate_test_cases(requirements)
    save_test_cases(test_cases, output_file)

    return test_cases