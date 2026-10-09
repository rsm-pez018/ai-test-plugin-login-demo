# AI Testing Agent Prototype

AI-assisted end-to-end API testing prototype built around a React + Flask login/register demo. The project validates the workflow from PRD analysis to executable tests, deterministic result comparison, Bug Report generation, and Test Report generation.

## What this project demonstrates

```text
PRD upload
→ requirement extraction
→ API test-case generation
→ test-case validation
→ deterministic API execution
→ Expected / Actual comparison
→ Bug Report
→ Test Report
```

The demo intentionally contains one business-rule bug: the PRD requires usernames to contain at least six characters, but the registration API does not enforce that rule.

## Current verification

The latest complete run contains:

```text
10 test cases
9 passed
1 failed
```

The failed case is the expected username-length defect in the registration API.

## Project structure

```text
.
├── backend/                  # Demo Flask API, port 5000
├── frontend/                 # Login/register Demo UI
├── platform-frontend/        # AI testing dashboard, port 5173
├── ai-agent/                 # Agent API and testing pipeline, port 5001
│   ├── agent_api.py
│   ├── run_agent.py
│   ├── config/
│   ├── prompts/
│   ├── skills/
│   └── outputs/
├── docs/
│   ├── PRD.md
│   ├── PLUGIN_ARCHITECTURE.md
│   ├── PLUGIN_ARCHITECTURE.en.md
│   └── final-run-2026-10-09/
└── HANDOFF.md
```

## Services and ports

| Port | Service | Purpose |
|---:|---|---|
| 5000 | Demo Backend | Target login/register API |
| 5001 | Agent API | Orchestrates the testing workflow |
| 5173 | Platform Frontend | Human-facing testing dashboard |

## Setup

### 1. Demo backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 2. Agent API

Copy `ai-agent/.env.example` to `ai-agent/.env`, then add an OpenAI API key locally. Never commit `.env`.

```bash
cd ai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent_api.py
```

Health check:

```bash
curl http://127.0.0.1:5001/api/health
```

### 3. Platform frontend

```bash
cd platform-frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Demo workflow

1. Upload `docs/PRD.md` in the platform frontend.
2. Configure the target API or load the Demo endpoints.
3. Run the full workflow.
4. Review Requirements, Test Cases, Execution, Analysis, Bug Report, and Test Report.
5. Expand table rows to inspect Raw JSON where available.

The Agent generates unique runtime usernames and passwords for each run. Login tests reuse the account created by the successful registration case. Reports use the actual execution records for test data, Expected, Actual, and statistics; LLMs are not used to decide PASS/FAIL.

## Documentation and artifacts

- [Chinese plugin architecture](docs/PLUGIN_ARCHITECTURE.md)
- [English plugin architecture](docs/PLUGIN_ARCHITECTURE.en.md)
- [Active PRD](docs/PRD.md)
- Final run artifacts: `docs/final-run-2026-10-09/`
- Latest generated artifacts: `ai-agent/outputs/`

## Security and prototype limitations

- Do not commit `.env`, API keys, virtual environments, `node_modules`, or SQLite databases.
- The demo stores passwords in plaintext and must not be used as a production authentication service.
- Flask development servers are for local testing only.
- Uploaded PRDs may contain sensitive product information; a real deployment needs access control, retention, and deletion policies.

## Future direction

The current project is an API-testing MVP. Future versions can add OpenAPI import, project/run isolation, authentication configuration, setup/teardown, additional API PRDs, Playwright browser execution, and Jira/GitHub integration.
