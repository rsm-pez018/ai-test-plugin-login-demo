# AI Testing Agent

An API-testing MVP that turns a PRD and target API contract into requirements,
test cases, executions, deterministic PASS/FAIL results, and reports.

## Project layout

- `backend/`: the login/register demo system under test.
- `ai-agent/`: Agent API, deterministic test modules, prompts, and run workspaces.
- `platform-frontend/`: the testing workspace UI.
- `docs/`: PRDs, examples, and project documentation.

## Local setup

Create a Python environment for each Python service, then install the Agent
dependencies:

```bash
cd ai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `ai-agent/.env` locally. Never commit that file.

Run the three services in separate terminals:

```bash
cd backend && source venv/bin/activate && python3 app.py
cd ai-agent && source venv/bin/activate && python3 agent_api.py
cd platform-frontend && npm install && npm run dev
```

The demo API runs on `http://127.0.0.1:5000`, the Agent API on
`http://127.0.0.1:5001`, and the platform UI on the Vite port shown by the
terminal.

## Run isolation

Each configured project is stored under `ai-agent/workspaces/<project_id>/`.
Every workflow run gets its own `runs/<run_id>/` directory containing input
snapshots, JSON outputs, reports, and an evidence directory. The active project
and run are recorded in `ai-agent/workspaces/.active.json`.

Runtime workspaces are intentionally ignored by Git. The checked-in sample
inputs remain under `docs/samples/`.

## Harness runtime

The full workflow is executed by `WorkflowRunner`. It writes run metadata and
JSONL events to each run directory:

```text
run.json       # lifecycle status
trace.jsonl    # stage start/success/failure and tool events
evidence/      # one redacted evidence file per API test
outputs/       # requirements, cases, execution and reports
```

The deterministic executor calculates PASS/FAIL. The model can assist with
planning and explanations, but it cannot override the verifier.

## Function Calling tools

The Agent API exposes:

- `GET /api/agent/tools`: list registered strict-schema tools.
- `POST /api/agent/tools/execute`: execute one allowlisted tool directly.
- `POST /api/agent/tools/run`: run a bounded Responses API tool loop.

The API executor only accepts configured HTTP(S) targets and relative endpoint
paths. Request evidence redacts passwords, tokens, authorization values, and
other secret-like fields.
