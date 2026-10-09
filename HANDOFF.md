# AI Testing Agent Project Handoff

Last updated: 2026-10-06

This document is written for a new conversation with no previous context. Read it before changing code.

## 1. What We Are Building

The project is an AI-assisted end-to-end testing prototype plus a small system under test.

The intended workflow is:

```text
Upload PRD
-> LLM extracts structured requirements
-> LLM generates API test cases
-> deterministic validator checks the generated cases
-> deterministic executor calls the target API
-> expected and actual results are compared
-> failed cases become a Bug Report
-> all results become a Test Report
```

The current system under test is a React + Flask login/register demo. It intentionally contains one business-rule bug: the PRD requires usernames to contain at least 6 characters, but the registration API does not enforce that rule.

This is currently an API-testing MVP. It assists a test engineer; it is not yet a general replacement for a test engineer, browser automation platform, or production plugin.

## 2. Important Terminology

- `frontend/`: the original login/register Demo being tested.
- `backend/`: the Demo API being tested, running on port `5000`.
- `ai-agent/`: the testing pipeline and its Agent API, running on port `5001`.
- `platform-frontend/`: the AI testing platform UI, normally running on port `5173`.
- `skills/`: Python modules used by this project. They are not Codex `SKILL.md` skills.
- `outputs/`: generated artifacts from the latest run. These files are overwritten by later runs.

The three ports are three services, not three test endpoints:

| Port | Service | Purpose |
|---|---|---|
| `5000` | Demo backend | Target system under test |
| `5001` | Agent API | Orchestrates the AI testing pipeline |
| `5173` | Platform frontend | Human-facing testing dashboard |

## 3. Current Architecture

```text
platform-frontend (React + Ant Design)
          |
          | HTTP
          v
ai-agent/agent_api.py (Flask, port 5001)
          |
          v
ai-agent/run_agent.py
          |
          +-- requirement_analyzer.py       LLM
          +-- test_case_generator.py        LLM
          +-- test_case_validator.py        deterministic validation
          +-- test_executor.py              deterministic HTTP execution
          +-- result_analyzer.py             deterministic comparison
          +-- bug_report_generator.py       LLM when failures exist
          +-- test_report_generator.py      LLM
          |
          v
backend/app.py (Demo Flask API, port 5000)
```

The hybrid design is intentional. LLMs handle interpretation and text generation; code handles schema validation, HTTP execution, and PASS/FAIL decisions. Do not move deterministic assertions into an LLM.

## 4. What Has Been Completed

### Demo system

- React login and registration UI exists.
- Flask registration and login APIs exist.
- SQLite stores users.
- Frontend and backend are connected.
- The intentional username-length bug is present.
- Password-required and password-minimum-length validation exist.

### Agent pipeline

- Markdown PRD input is supported.
- LLM-based requirement extraction is implemented.
- LLM-based API test-case generation is implemented.
- Generated test cases are validated before execution.
- Tests are executed against configured HTTP endpoints.
- Actual status codes and messages are compared with expected values.
- Failed cases are collected and analyzed.
- Markdown Bug Reports are generated.
- Markdown Test Reports are generated.
- Positive registration and positive login cases are included.
- Randomized usernames are used to reduce collisions with existing SQLite users.

### Agent API

`ai-agent/agent_api.py` exposes:

- `GET /api/health`
- `POST /api/project/upload-prd`
- `POST /api/project/configure-target`
- `POST /api/agent/analyze-requirements`
- `POST /api/agent/generate-test-cases`
- `POST /api/agent/execute-tests`
- `POST /api/agent/generate-reports`
- `POST /api/agent/run-all`

The PRD upload endpoint currently accepts UTF-8 `.md` and `.txt` files. It does not directly parse PDF or WPS files.

### Platform UI

- A React + Ant Design dashboard exists in `platform-frontend/`.
- Users can upload a PRD and configure a target API.
- Users can run individual pipeline stages or the full pipeline.
- The UI displays requirements, test cases, execution results, analysis, Bug Report, and Test Report.
- Execution results are shown in a readable table.
- Markdown reports are rendered in the browser.

### Documentation and samples

- Active PRD: `docs/PRD.md`
- Backup sample PRD: `docs/samples/login_register_prd.md`
- Sample API configuration: `docs/samples/login_register_target_api.json`
- Manual requirements, test cases, execution records, Bug Report, and Test Report exist under `docs/`.

## 5. Current Verified Result

The active login/register configuration contains two target endpoints:

- `POST /api/register`
- `POST /api/login`

The latest expected pipeline result is:

| Item | Count |
|---|---:|
| Extracted requirements | 8 |
| Generated test cases | 10 |
| Executed test cases | 10 |
| Passed | 9 |
| Failed | 1 |

The intended failed case is the short-username registration test:

```text
Expected: HTTP 400, username must contain at least 6 characters
Actual:   HTTP 200, registration succeeds
```

Ten test cases are expected because the eight extracted rules are supplemented by successful registration and successful login cases.

At handoff time, Python syntax compilation passed for the backend, Agent API, orchestrator, and all Agent skills. The platform frontend production build also passed. Vite reported only a large JavaScript bundle warning, not a build failure.

## 6. Key Files

```text
AI-Testing-Agent/
├── HANDOFF.md
├── backend/
│   ├── app.py
│   ├── users.db
│   └── venv/
├── frontend/                       # Login/register Demo UI
├── platform-frontend/              # AI testing dashboard
│   ├── src/
│   └── package.json
├── docs/
│   ├── PRD.md                      # Active PRD, overwritten by upload
│   ├── samples/
│   │   ├── login_register_prd.md
│   │   └── login_register_target_api.json
│   └── other manual test documents
└── ai-agent/
    ├── .env                        # Contains secret; never commit or print
    ├── agent_api.py
    ├── run_agent.py
    ├── config/
    │   └── target_api.json         # Active target configuration
    ├── prompts/
    │   ├── requirement_analyzer_prompt.md
    │   ├── test_case_generator_prompt.md
    │   ├── bug_report_generator_prompt.md
    │   └── test_report_generator_prompt.md
    ├── skills/
    │   ├── requirement_analyzer.py
    │   ├── test_case_generator.py
    │   ├── test_case_validator.py
    │   ├── test_executor.py
    │   ├── result_analyzer.py
    │   ├── bug_report_generator.py
    │   └── test_report_generator.py
    └── outputs/
        ├── requirements_ai.json
        ├── test_cases_ai.json
        ├── test_execution_ai.json
        ├── result_analysis_ai.json
        ├── bug_report_ai.md
        └── test_report_ai.md
```

## 7. How To Run It

Use three named VS Code terminals.

### Terminal 1: Demo Backend

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/backend
source venv/bin/activate
python3 app.py
```

Expected service: `http://127.0.0.1:5000`

Opening the bare URL in a browser may show `404 Not Found`. That is normal because the Demo defines API routes rather than a `/` webpage.

### Terminal 2: Agent API

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/ai-agent
source venv/bin/activate
python3 agent_api.py
```

Expected service: `http://127.0.0.1:5001`

Health check:

```bash
curl http://127.0.0.1:5001/api/health
```

### Terminal 3: Platform Frontend

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/platform-frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Do not run `frontend/` and `platform-frontend/` on the same default Vite port at the same time. They are different applications.

### Optional CLI run

With the Demo backend running:

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/ai-agent
source venv/bin/activate
python3 run_agent.py
```

## 8. Current Position / What Is Blocking Progress

There is no known hard runtime blocker. The MVP works. The project is now at the transition from a single-demo prototype to a reusable testing platform.

The main gaps are:

1. The Requirements and Test Cases views still expose too much raw JSON. They should be readable tables or structured panels.
2. The app uses global active files (`docs/PRD.md`, one target config, one output directory). A new run overwrites the previous run.
3. Some report metadata and assumptions remain specific to the login/register Demo.
4. A new PRD alone is not enough to test an arbitrary system. The user must also provide its API contract/configuration, endpoints, methods, request fields, and expected responses.
5. There is no OpenAPI import yet.
6. There is no browser/UI execution with Playwright yet.
7. Bug reports are generated as Markdown but are not pushed to GitHub Issues or Jira.
8. Reproducible project setup is incomplete: there is no root README, root `.gitignore`, or Python dependency file.
9. The directory is currently not a Git repository, so GitHub upload requires initializing Git or cloning/connecting the intended repository first.

## 9. Recommended Next Plan

Follow this order. Do not jump straight to Playwright or deployment.

### Phase 1: Secure and make the project reproducible

1. Add a root `.gitignore` covering:
   - `.env`
   - `venv/`
   - `node_modules/`
   - `__pycache__/`
   - `*.pyc`
   - `users.db`
   - local generated/runtime files as appropriate
2. Add `.env.example` without a real key.
3. Add Python dependency files for `backend/` and `ai-agent/`.
4. Add a root `README.md` with architecture and startup commands.
5. Audit for secrets before creating the Git repository or pushing to GitHub.

### Phase 2: Finish the platform UI

1. Replace raw Requirements JSON with a table containing ID, module, field, rule, and expected behavior.
2. Replace raw Test Cases JSON with a table or expandable rows containing scenario, endpoint, method, test data, expected result, and priority.
3. Add clear running, success, and failure states for every stage.
4. Add download buttons for JSON and Markdown artifacts.
5. Keep technical raw JSON in an optional developer view rather than the primary user view.

### Phase 3: Generalize the backend

1. Introduce `project_id` and `run_id`.
2. Store each run in its own directory instead of overwriting global outputs.
3. Store the uploaded PRD and target configuration per project.
4. Add OpenAPI/Swagger import to reduce manual target configuration.
5. Add setup/teardown and test dependencies, such as creating a user before testing successful login.
6. Remove login/register-specific report metadata and assumptions.

### Phase 4: Improve reliability

1. Use strict structured output schemas for LLM results.
2. Validate LLM output before saving it.
3. Add timeouts, retries, and useful error messages for OpenAI and target API calls.
4. Avoid leaving half-written output files when a stage fails.
5. Make assertions configurable; exact message equality is currently brittle.
6. Remove the duplicate application-start block in `backend/app.py`.

### Phase 5: Evaluate the Agent

Build a small evaluation set with multiple PRDs and known bugs. Measure:

- requirement extraction accuracy
- test-case validity rate
- requirement coverage
- execution success rate
- bug precision and recall
- false-positive rate
- latency
- token/API cost

### Phase 6: Extend the product

1. Add Playwright for browser workflows.
2. Add human review/approval before risky runs or external Bug submission.
3. Add GitHub Issues or Jira integration.
4. Add authentication, persistence, and deployment only after project/run isolation works.

## 10. Pitfalls Already Encountered

Do not repeat these mistakes:

1. **Starting the Agent API twice**
   - `Address already in use` on port `5001` means an Agent API process is already running.
   - Stop the old process with `Ctrl+C` or use the existing terminal; do not keep creating servers.

2. **Treating a backend API as a normal webpage**
   - `http://127.0.0.1:5000/` can return 404 while `/api/register` and `/api/login` still work correctly.

3. **Confusing the two frontends**
   - `frontend/` is the tested Demo.
   - `platform-frontend/` is the testing tool.

4. **Uploading only one endpoint configuration**
   - `endpoint_count: 1` means only one endpoint is available to the generator.
   - Registration and login coverage requires both endpoints in the `endpoints` array.

5. **Assuming any PRD can run without an API contract**
   - The PRD explains business behavior.
   - The target configuration explains how to call the real system.
   - Both are required for executable API tests.

6. **Username collisions in SQLite**
   - Reusing a successful registration username causes `Username already exists` and can create a misleading failure.
   - Keep randomized test data or reset isolated test data between runs.

7. **Overwriting the active PRD**
   - Uploading a PRD replaces `docs/PRD.md`.
   - Preserve canonical examples under `docs/samples/`.

8. **Exposing the API key**
   - `ai-agent/.env` contains the OpenAI key.
   - Never display, paste, log, or commit it.
   - OpenAI API usage is billed separately from ChatGPT subscriptions.

9. **Committing runtime directories and state**
   - Do not commit `venv`, `node_modules`, SQLite runtime data, caches, or secrets.

10. **Misreading the LibreSSL warning as the main failure**
    - The Python 3.9/urllib3 LibreSSL warning has been nonfatal.
    - Eventually use a newer Homebrew Python and recreate the virtual environment, but inspect the final traceback line first when debugging.

11. **Parsing LLM text as guaranteed JSON**
    - Models may wrap JSON in Markdown fences or return malformed structures.
    - Keep fence cleanup and add schema validation/structured outputs.

12. **Using an LLM to decide PASS/FAIL**
    - PASS/FAIL should remain deterministic based on expected and actual data.

13. **Assuming terminal output is separate from output files**
    - The terminal is a display of the run.
    - Files in `ai-agent/outputs/` are the persistent artifacts for the latest run.

14. **VS Code save conflicts**
    - A save conflict means the file changed on disk after the editor opened it.
    - Compare both versions and keep the intended merged version; do not blindly overwrite.

## 11. Security and Data Notes

- Never read the `.env` value into chat output.
- Rotate the OpenAI key if it was ever exposed.
- Passwords are stored in plaintext in the Demo database. This is acceptable only for this local testing prototype and must be called out clearly.
- The Flask development servers are not production servers.
- Uploaded PRDs may contain sensitive product information; a real deployment needs access control, retention rules, and deletion controls.

## 12. What “General Purpose” Should Mean Here

The Agent should not contain Python branches such as “if this is the registration username rule, generate this exact case” for every future product rule.

A reusable version should accept:

1. A PRD describing expected business behavior.
2. An API contract/configuration describing callable operations.
3. Optional environment variables, authentication, test-data setup, and cleanup rules.

The LLM maps requirements to test ideas and structured cases. Validators ensure that generated cases match the available API contract. The executor remains generic and deterministic.

Different systems do not always have webpages. The platform must be able to test APIs directly. Browser-based products can later use a separate Playwright executor.

## 13. First Actions for the Next Conversation

The next conversation should begin with these commands, without opening or printing `.env`:

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent
git status
find . -maxdepth 2 -type f | sort
```

If Git reports that this is not a repository, do not push anything yet. First add `.gitignore`, `.env.example`, dependency files, and README, then initialize or connect the repository only after checking that no secret is tracked.

The best next coding task is to make the Requirements and Test Cases tabs human-readable while preserving an optional raw JSON view. After that, implement project/run isolation before adding more testing capabilities.
