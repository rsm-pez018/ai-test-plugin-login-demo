from flask import Flask, jsonify, request
from pathlib import Path
from flask_cors import CORS
import json

from run_agent import (
    run_all,
    analyze_requirements,
    generate_test_cases,
    execute_tests,
    generate_reports,
    load_target_config,
    OUTPUT_FILE
)


app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRD_FILE = PROJECT_ROOT / "docs" / "PRD.md"
TARGET_API_CONFIG_FILE = (
    PROJECT_ROOT / "ai-agent" / "config" / "target_api.json"
)

ALLOWED_PRD_EXTENSIONS = {".md", ".txt"}

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "AI Testing Agent API"
    })

@app.post("/api/project/upload-prd")
def upload_prd_endpoint():
    try:
        if "file" not in request.files:
            return jsonify({
                "status": "error",
                "message": "No PRD file provided"
            }), 400

        uploaded_file = request.files["file"]

        if uploaded_file.filename == "":
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400

        extension = Path(uploaded_file.filename).suffix.lower()

        if extension not in ALLOWED_PRD_EXTENSIONS:
            return jsonify({
                "status": "error",
                "message": "Only .md and .txt files are supported"
            }), 400

        prd_text = uploaded_file.read().decode("utf-8")
        PRD_FILE.write_text(prd_text, encoding="utf-8")

        return jsonify({
            "status": "success",
            "filename": uploaded_file.filename,
            "saved_to": str(PRD_FILE)
        }), 200

    except UnicodeDecodeError:
        return jsonify({
            "status": "error",
            "message": "The PRD file must use UTF-8 encoding"
        }), 400

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

@app.post("/api/project/configure-target")
def configure_target_endpoint():
    try:
        config = request.get_json(silent=True)

        if not config:
            return jsonify({
                "status": "error",
                "message": "JSON body is required"
            }), 400

        required_fields = ["project_name", "base_url", "endpoints"]
        missing_fields = [
            field for field in required_fields
            if not config.get(field)
        ]

        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing fields: {', '.join(missing_fields)}"
            }), 400

        if not isinstance(config["endpoints"], list):
            return jsonify({
                "status": "error",
                "message": "endpoints must be a list"
            }), 400

        for index, endpoint in enumerate(config["endpoints"]):
            required_endpoint_fields = [
                "name",
                "path",
                "method",
                "request_body",
                "expected_responses"
            ]

            missing_endpoint_fields = [
                field for field in required_endpoint_fields
                if field not in endpoint
            ]

            if missing_endpoint_fields:
                return jsonify({
                    "status": "error",
                    "message": (
                        f"Endpoint {index + 1} is missing: "
                        f"{', '.join(missing_endpoint_fields)}"
                    )
                }), 400

        TARGET_API_CONFIG_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        TARGET_API_CONFIG_FILE.write_text(
            json.dumps(config, indent=2),
            encoding="utf-8"
        )

        return jsonify({
            "status": "success",
            "message": "Target API configuration saved",
            "saved_to": str(TARGET_API_CONFIG_FILE),
            "endpoint_count": len(config["endpoints"])
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

@app.post("/api/agent/analyze-requirements")
def analyze_requirements_endpoint():
    try:
        requirements = analyze_requirements()

        return jsonify({
            "status": "success",
            "count": len(requirements),
            "requirements": requirements
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500
@app.post("/api/agent/generate-test-cases")

def generate_test_cases_endpoint():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            requirements = json.load(file)

        target_config = load_target_config()

        test_cases = generate_test_cases(
            requirements,
            target_config
        )

        return jsonify({
            "status": "success",
            "count": len(test_cases),
            "test_cases": test_cases
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


@app.post("/api/agent/execute-tests")
def execute_tests_endpoint():
    try:
        target_config = load_target_config()
        execution_results = execute_tests(target_config)

        return jsonify({
            "status": "success",
            "count": len(execution_results),
            "execution_results": execution_results
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

@app.post("/api/agent/generate-reports")
def generate_reports_endpoint():
    try:
        report_result = generate_reports()

        return jsonify({
            "status": "success",
            "data": report_result
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

@app.post("/api/agent/run-all")
def run_all_endpoint():
    try:
        result = run_all()

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
