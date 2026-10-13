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
)
from workspace import (
    activate_project,
    activate_run,
    get_active_workspace,
    save_project_prd,
    save_target_config,
)
from agent_tools import FUNCTION_TOOLS, execute_tool
from function_calling import run_function_calling
from harness import WorkflowRunner


app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
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
        project_name = request.form.get("project_name", "default-project")
        project_id = activate_project(project_name)
        prd_path = save_project_prd(project_id, prd_text)

        return jsonify({
            "status": "success",
            "filename": uploaded_file.filename,
            "project_id": project_id,
            "saved_to": str(prd_path)
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

        project_id = activate_project(config["project_name"])
        config_path = save_target_config(project_id, config)

        return jsonify({
            "status": "success",
            "message": "Target API configuration saved",
            "project_id": project_id,
            "saved_to": str(config_path),
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
        workspace = get_active_workspace()
        runner = WorkflowRunner(workspace)
        requirements = runner.run_stage(
            "analyze_requirements",
            lambda: analyze_requirements(workspace),
        )

        return jsonify({
            "status": "success",
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
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
        workspace = get_active_workspace()
        runner = WorkflowRunner(workspace)
        requirements_file = workspace.output_dir / "requirements_ai.json"
        with open(requirements_file, "r", encoding="utf-8") as file:
            requirements = json.load(file)

        target_config = load_target_config(workspace)

        test_cases = runner.run_stage(
            "generate_and_validate_test_cases",
            lambda: generate_test_cases(
                requirements,
                target_config,
                workspace,
            ),
        )

        return jsonify({
            "status": "success",
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
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
        workspace = get_active_workspace()
        runner = WorkflowRunner(workspace)
        target_config = load_target_config(workspace)
        execution_results = runner.run_stage(
            "execute_tests",
            lambda: execute_tests(target_config, workspace),
        )

        return jsonify({
            "status": "success",
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
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
        workspace = get_active_workspace()
        runner = WorkflowRunner(workspace)
        report_result = runner.run_stage(
            "generate_reports",
            lambda: generate_reports(workspace),
        )

        return jsonify({
            "status": "success",
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
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
        workspace = get_active_workspace()
        result = run_all(workspace)

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


@app.get("/api/agent/tools")
def list_tools_endpoint():
    return jsonify({
        "status": "success",
        "tools": FUNCTION_TOOLS,
    }), 200


@app.post("/api/agent/tools/execute")
def execute_tool_endpoint():
    try:
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        arguments = payload.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, dict):
            return jsonify({
                "status": "error",
                "message": "name must be a string and arguments must be an object",
            }), 400

        workspace = get_active_workspace()
        result = execute_tool(name, arguments, workspace)
        return jsonify({
            "status": "success",
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
            "tool": name,
            "result": result,
        }), 200
    except ValueError as error:
        return jsonify({"status": "error", "message": str(error)}), 400
    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500


@app.post("/api/agent/tools/run")
def run_tools_endpoint():
    try:
        payload = request.get_json(silent=True) or {}
        goal = payload.get("goal")
        if not isinstance(goal, str) or not goal.strip():
            return jsonify({
                "status": "error",
                "message": "goal must be a non-empty string",
            }), 400
        workspace = get_active_workspace()
        result = run_function_calling(goal, workspace)
        return jsonify({
            "status": "success",
            "project_id": workspace.project_id,
            "run_id": workspace.run_id,
            "data": result,
        }), 200
    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
