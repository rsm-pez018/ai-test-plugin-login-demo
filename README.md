# AI Testing Agent Demo - Login/Register System

This project is a small React + Flask demo used to verify an AI-assisted testing workflow. The demo includes a basic registration and login flow, testing documents, an AI testing agent prototype, a test report, and a bug report.

The key purpose of this project is not only to build a login/register system, but also to show a complete testing process from requirement analysis to bug reporting.

## Tech Stack

- Frontend: React, Vite, Axios, React Router
- Backend: Flask, SQLite
- Testing: Browser testing, API testing, test cases, test report, bug report
- AI Agent Prototype: Python, API testing, structured JSON/Markdown outputs

## Features

- User registration
- User login
- Login success page
- Basic backend validation
- SQLite user storage

## Intentional Bug

The requirement states that username length must be at least 6 characters.

However, the backend registration API intentionally does not validate username length. This is used as a known bug for testing:

```text
BUG_REGISTER_001 - Username length validation is missing in the registration API
```

## Project Structure

```text
.
├── backend
│   ├── app.py
│   └── requirements.txt
├── docs
│   ├── PRD.pdf
│   ├── PRD.wps
│   ├── bug_report(human test).md
│   ├── login_test_cases.md
│   ├── login_test_execution.md
│   ├── register_requirement.md
│   ├── test_cases.md
│   ├── test_execution.md
│   └── test_report.md
├── ai-agent
│   ├── run_agent.py
│   ├── requirements.txt
│   ├── skills
│   │   ├── requirement_analyzer.py
│   │   ├── test_case_generator.py
│   │   ├── test_executor.py
│   │   ├── result_analyzer.py
│   │   ├── bug_report_generator.py
│   │   └── test_report_generator.py
│   └── outputs
│       ├── requirements_ai.json
│       ├── test_cases_ai.json
│       ├── test_execution_ai.json
│       ├── result_analysis_ai.json
│       ├── bug_report_ai.md
│       └── test_report_ai.md
└── frontend
    ├── package.json
    ├── src
    └── vite.config.js
```

## How to Run

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

### AI Testing Agent

Keep the Flask backend running first, then open another terminal:

```bash
cd ai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_agent.py
```

The agent runs this workflow:

```text
Requirement Analyzer
→ Test Case Generator
→ Test Executor
→ Result Analyzer
→ Bug Report Generator
→ Test Report Generator
```

`run_agent.py` acts as the workflow controller. Each file under `ai-agent/skills/` is an independent skill module for one step of the testing workflow.

Generated outputs are saved in:

```text
ai-agent/outputs/
```

The agent calls the Flask API directly, so the frontend page does not need to be opened while running the agent.

## Test Result

Manual testing result:

Total test cases: 7

- Passed: 6
- Failed: 1

The failed case is `TC_REGISTER_004`, where a username shorter than 6 characters can still be registered successfully.

See the full report in:

```text
docs/test_report.md
```

AI-generated test outputs are available in:

```text
ai-agent/outputs/test_report_ai.md
ai-agent/outputs/bug_report_ai.md
```

Latest AI agent run:

```text
Total test cases: 5
Passed: 4
Failed: 1
```
