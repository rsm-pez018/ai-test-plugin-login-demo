import json
import uuid
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = OpenAI()


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def parse_json_output(output_text):
    cleaned_text = output_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.removeprefix("```json").strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```").strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.removesuffix("```").strip()

    return json.loads(cleaned_text)


def apply_runtime_test_data(test_cases, runtime_test_data):
    """Replace model-provided example credentials with this run's unique data."""
    valid_username = runtime_test_data["valid_username"]
    valid_password = runtime_test_data["valid_password"]
    short_username = runtime_test_data["short_username"]
    password_test_username = runtime_test_data["password_test_username"]
    non_existing_username = runtime_test_data["non_existing_username"]
    wrong_password = runtime_test_data["wrong_password"]

    for test_case in test_cases:
        test_data = test_case.get("test_data")
        if not isinstance(test_data, dict):
            continue

        scenario = test_case.get("scenario", "").lower()
        requirement_id = test_case.get("related_requirement_id", "").lower()

        if "empty username" in scenario or "username is required" in requirement_id:
            test_data["username"] = ""
        elif any(term in scenario for term in ("less than 6", "shorter than 6", "minimum-length")):
            test_data["username"] = short_username
        elif "non-existent username" in scenario or "does not exist" in scenario:
            test_data["username"] = non_existing_username
        elif "successful" in scenario or "valid username" in scenario:
            test_data["username"] = valid_username
        elif "password" in scenario or "password" in requirement_id:
            test_data["username"] = password_test_username if "registration" in scenario else valid_username

        if "empty password" in scenario or "password is required" in requirement_id:
            test_data["password"] = ""
        elif "password" in scenario and any(term in scenario for term in ("less than 6", "shorter than 6", "minimum-length")):
            test_data["password"] = "12345"
        elif "incorrect password" in scenario or "wrong password" in scenario:
            test_data["password"] = wrong_password
        elif "successful" in scenario or "valid password" in scenario:
            test_data["password"] = valid_password

    return test_cases


def generate_test_cases(requirements, api_config, prompt_text):
    run_id = uuid.uuid4().hex[:8]
    valid_username = f"user{run_id}"
    valid_password = f"Valid{run_id}9"
    short_username = f"u{run_id[:4]}"
    password_test_username = f"pass{run_id}"
    non_existing_username = f"nonexistent{run_id}"
    wrong_password = f"Wrong{run_id}9"

    generation_context = {
        "requirements": requirements,
        "api_config": api_config,
        "unique_suffix": run_id,
        "runtime_test_data": {
            "valid_username": valid_username,
            "valid_password": valid_password,
            "short_username": short_username,
            "password_test_username": password_test_username,
            "non_existing_username": non_existing_username,
            "wrong_password": wrong_password
        }
    }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"{prompt_text}\n\nInput JSON:\n{json.dumps(generation_context, indent=2)}"
    )

    test_cases = parse_json_output(response.output_text)
    return apply_runtime_test_data(test_cases, generation_context["runtime_test_data"])

def save_test_cases(test_cases, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(test_cases, file, indent=2)


def run(requirements, output_file, prompt_file, api_config_file):
    prompt_text = read_file(prompt_file)
    api_config = read_json(api_config_file)

    test_cases = generate_test_cases(
        requirements,
        api_config,
        prompt_text
    )

    save_test_cases(test_cases, output_file)

    return test_cases
