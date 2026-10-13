import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = OpenAI()


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def analyze_with_llm(requirement_text, prompt_text):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"{prompt_text}\n\nPRD Document:\n{requirement_text}"
    )

    return json.loads(response.output_text)


def save_requirements(requirements, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(requirements, file, indent=2)


def run(requirement_file, output_file, prompt_file):
    requirement_text = read_file(requirement_file)
    prompt_text = read_file(prompt_file)

    requirements = analyze_with_llm(requirement_text, prompt_text)
    save_requirements(requirements, output_file)

    return requirements
