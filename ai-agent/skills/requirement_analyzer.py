import json


def read_requirement_file(requirement_file):
    with open(requirement_file, "r", encoding="utf-8") as file:
        return file.read()


def analyze_requirements(requirement_text):
    text = requirement_text.lower()
    requirements = []

    if "username" in text:
        requirements.append({
            "requirement_id": "REQ_REGISTER_001",
            "module": "Register",
            "field": "username",
            "rule": "Username is required",
            "expected_behavior": "Registration should fail when username is empty"
        })

        requirements.append({
            "requirement_id": "REQ_REGISTER_002",
            "module": "Register",
            "field": "username",
            "rule": "Username length must be greater than or equal to 6 characters",
            "expected_behavior": "Registration should fail when username length is less than 6 characters"
        })

    if "password" in text:
        requirements.append({
            "requirement_id": "REQ_REGISTER_003",
            "module": "Register",
            "field": "password",
            "rule": "Password is required",
            "expected_behavior": "Registration should fail when password is empty"
        })

        requirements.append({
            "requirement_id": "REQ_REGISTER_004",
            "module": "Register",
            "field": "password",
            "rule": "Password length must be greater than or equal to 6 characters",
            "expected_behavior": "Registration should fail when password length is less than 6 characters"
        })

    return requirements


def save_requirements(requirements, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(requirements, file, indent=2)


def run(requirement_file, output_file):
    requirement_text = read_requirement_file(requirement_file)
    requirements = analyze_requirements(requirement_text)
    save_requirements(requirements, output_file)

    return requirements