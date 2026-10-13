# AI Testing Agent 项目交接文档

最后更新：2026-10-12

> 给没有历史上下文的新会话阅读。本文只记录项目开发和验证进度，不包含简历修改内容。

## 1. 我们在做什么

这是一个“AI 驱动的自动化测试 Agent”最小可验证原型，目标是验证下面这条端到端链路：

```text
上传 PRD
→ 需求分析与结构化
→ API 测试用例生成
→ 测试用例校验
→ 调用被测 API
→ Expected / Actual 对比
→ PASS / FAIL 判断
→ Bug Report 生成
→ Test Report 生成
```

当前使用一个 React + Flask 登录注册 Demo 作为被测系统（System Under Test）。Demo 中刻意保留了一个业务规则 Bug：PRD 要求用户名至少 6 位，但注册接口没有正确执行该限制。Agent 应该能够通过测试发现这个 Bug。

当前定位是 API 测试 MVP，不是生产级插件，也不是浏览器自动化平台。LLM 负责理解 PRD 和生成测试设计；确定性程序负责校验、HTTP 调用和 PASS/FAIL 判断。

## 2. 当前项目目录与服务

真正的活动工作目录是：

```text
/Users/peipe/Desktop/AI-Testing-Agent
```

目录职责：

| 目录 | 作用 | 默认端口 |
|---|---|---:|
| `backend/` | 被测登录注册 Flask API | 5000 |
| `frontend/` | 原始登录注册 Demo 前端 | Vite 默认端口 |
| `ai-agent/` | Agent API、编排器、Python skills 和运行产物 | 5001 |
| `platform-frontend/` | AI 测试平台工作台 | 5173 |
| `docs/` | PRD、架构文档、人工测试文档和样例 | - |

重要区分：

- `frontend/` 是被测试的 Demo 前端。
- `platform-frontend/` 是 AI Testing Workspace 测试平台前端。
- `ai-agent/skills/*.py` 是本项目的 Python 模块，不是 Codex 的 `SKILL.md` 技能。
- `ai-agent/.env` 含有 API 密钥，绝对不能读取、打印或提交。

### Git / GitHub 注意事项

当前活动目录 `/Users/peipe/Desktop/AI-Testing-Agent` 本身没有 `.git` 目录。另有一个 Git clone：

```text
/Users/peipe/Documents/Playground/ai-test-plugin-login-demo
```

这个 clone 当前是旧版本，不能直接当作活动目录继续开发；它缺少活动目录中的完整 `platform-frontend/`、Agent API 等最新结构。后续如果要同步 GitHub，必须先明确要把哪个目录作为正式仓库，并检查密钥、虚拟环境、数据库和构建目录后再操作。

## 3. 已经完成的内容

### 被测登录注册 Demo

- React 登录、注册页面已存在。
- Flask 已实现 `POST /api/register` 和 `POST /api/login`。
- SQLite 用于本地数据存储。
- 注册和登录接口已经可以被 Agent 调用。
- 用户名长度 Bug 被保留，作为 Agent 发现缺陷的验证样例。
- 空用户名、空密码、密码长度等校验规则已存在。

### Agent 后端与 Python 模块

`ai-agent/agent_api.py` 已提供：

- `GET /api/health`
- `POST /api/project/upload-prd`
- `POST /api/project/configure-target`
- `POST /api/agent/analyze-requirements`
- `POST /api/agent/generate-test-cases`
- `POST /api/agent/execute-tests`
- `POST /api/agent/generate-reports`
- `POST /api/agent/run-all`

核心模块位于 `ai-agent/skills/`：

- `requirement_analyzer.py`：使用 LLM 从 PRD 提取结构化需求。
- `test_case_generator.py`：根据需求和 API 合约生成测试用例及运行时数据。
- `test_case_validator.py`：确定性检查字段、接口和测试数据结构。
- `test_executor.py`：确定性调用目标 HTTP API 并保存实际响应。
- `result_analyzer.py`：确定性比较 Expected / Actual 并计算 PASS/FAIL。
- `bug_report_generator.py`：根据失败执行记录生成 Bug Report。
- `test_report_generator.py`：根据执行记录生成 Test Report 和统计数据。

报告生成已经改为以真实执行记录为依据，不让 LLM 编造 Expected、Actual 或统计数字。

### 平台前端

`platform-frontend/` 已实现：

- PRD 上传。
- 项目名称、被测系统 Base URL 配置。
- API endpoint、请求体和 Expected responses 配置。
- 单步执行四个阶段。
- `Run full workflow` 一键运行完整流程。
- Requirements 人类可读表格。
- Test Cases 人类可读表格。
- 表格展开后可查看单条记录的 Raw JSON。
- Execution 结果表格。
- Analysis 失败用例表格和统计。
- Bug Report / Test Report Markdown 渲染。
- Agent API 连接状态、运行中状态和错误提示。
- 浏览器 `localStorage` 暂存当前会话结果，刷新后可保留最近结果。

Requirements/Test Cases 从原始 JSON 改成人类可读表格，同时保留可选 Raw JSON 视图，这个用户需求已经完成。

### 文档与测试产物

已存在：

- `docs/PRD.md`：当前活动 PRD。
- `docs/samples/login_register_prd.md`：登录注册样例 PRD。
- `docs/samples/login_register_target_api.json`：样例 API 合约。
- `docs/PLUGIN_ARCHITECTURE.md`：中文架构文档。
- `docs/PLUGIN_ARCHITECTURE.en.md`：英文架构文档。
- `docs/PRD_upload_test.md`：PRD 上传测试记录。
- `docs/test_cases.md`、`docs/test_execution.md`、`docs/test_report.md`：测试相关文档。
- `ai-agent/outputs/`：最近一次运行的 JSON、Bug Report 和 Test Report。

## 4. 当前已验证结果

当前活动配置包含 2 个 API endpoint：

- `POST /api/register`
- `POST /api/login`

最近一次完整运行结果：

| 项目 | 数量 |
|---|---:|
| 提取需求 | 8 |
| 生成测试用例 | 10 |
| 执行测试用例 | 10 |
| 通过 | 9 |
| 失败 | 1 |

失败用例：`TC-REGISTER-002`

```text
场景：用户名少于 6 位时注册失败
Expected：HTTP 400，Username length must be at least 6 characters
Actual：HTTP 200，Registration_successful
结论：识别出被测注册接口没有执行用户名最小长度校验
```

也就是说，当前 Demo 的“9 通过、1 失败”是预期结果，不是 Agent 流程本身失败。失败用例正是为了证明预埋 Bug 能被发现。

目前没有可靠的人工基线时间和 Agent 总耗时记录，因此不要在项目材料中写未经测量的“效率提升 XX%”。现有可使用的量化证据是 2 个 endpoint、4 个工作流阶段、10 个用例、9/10 通过和 1 个识别出的 Bug。

## 5. 当前卡点 / 未完成事项

没有已知的硬性运行阻塞，MVP 已经可以启动、运行和展示结果。当前主要是从单 Demo 原型走向可复用平台时的技术债：

1. 活动目录没有 Git 仓库，需要后续谨慎同步到 GitHub。
2. `ai-agent/.env`、`venv/`、`node_modules/`、SQLite 数据库和 `dist/` 需要在版本控制中排除。
3. PRD 和输出使用全局文件路径，新的项目/运行会覆盖旧结果，尚未实现 `project_id` / `run_id` 隔离。
4. API 合约需要手动配置，还没有 OpenAPI / Swagger 导入。
5. 当前主要支持 API 测试，还没有 Playwright 浏览器/UI 自动化。
6. Bug Report 还没有推送到 Jira 或 GitHub Issues。
7. 当前 PRD 上传主要支持 `.md` 和 `.txt`；PDF/WPS 需要先转换成文本或后续增加解析能力。
8. 当前密码在本地 Demo 数据库中明文保存，仅适用于本地原型，不能作为生产实现。
9. 没有执行耗时、Token 消耗、API 成本等指标采集。
10. `backend/app.py` 中存在重复的 `app.run()` 启动代码，当前不一定阻塞运行，但后续应清理。

## 6. 下一步计划

### 优先级 1：稳定当前 MVP

1. 给活动目录补充根目录 `.gitignore`，排除 `.env`、`venv/`、`node_modules/`、`__pycache__/`、`*.pyc`、`*.db` 和 `dist/`。
2. 添加不含真实密钥的 `ai-agent/.env.example`。
3. 补充根目录 `README.md` 和后端/Agent 的依赖文件。
4. 重新运行一次完整流程，确认 8/10/10/9/1 结果和前端各 Tab 展示正常。
5. 清理重复启动代码，并保留健康检查和清晰错误提示。

### 优先级 2：让项目真正可复用

1. 引入 `project_id` 和 `run_id`，每个项目和每次运行保存到独立目录。
2. 保存上传的 PRD、API 合约和运行产物，不再覆盖唯一的全局文件。
3. 把登录注册专属的报告标题、假设和字段改成通用配置。
4. 增加 OpenAPI/Swagger 导入，减少用户手动填写 endpoint 的工作量。
5. 增加测试数据 setup/teardown 和测试依赖，例如先注册用户再执行成功登录。

### 优先级 3：扩大测试能力

1. 增加 Playwright executor，支持网页流程测试。
2. 支持认证信息、环境变量、Header 和不同测试环境。
3. 增加人工审核后再提交 Bug 的流程。
4. 增加 Jira/GitHub Issues 集成。
5. 建立多份 PRD 和已知 Bug 的评测集，记录需求提取准确率、用例有效率、需求覆盖率、Bug precision/recall、延迟和成本。

不要直接跳到生产部署或复杂的多系统兼容。先完成项目/运行隔离和可复现启动，再扩展 Playwright 与外部 Bug 系统。

## 7. 启动方式

请使用三个 VS Code Terminal。不要把密钥粘贴到聊天或终端输出中。

### Terminal 1：被测 Demo 后端

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/backend
source venv/bin/activate
python3 app.py
```

服务地址：`http://127.0.0.1:5000`

访问根路径 `/` 出现 404 是正常的，因为这个服务主要提供 API 路由；应测试 `/api/register` 和 `/api/login`。

### Terminal 2：Agent API

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/ai-agent
source venv/bin/activate
python3 agent_api.py
```

服务地址：`http://127.0.0.1:5001`

健康检查：

```bash
curl http://127.0.0.1:5001/api/health
```

### Terminal 3：测试平台前端

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent/platform-frontend
npm install
npm run dev
```

打开：`http://localhost:5173`

如果点击 Run full workflow 出现 Network Error，先确认 5000、5001 两个后端服务都在运行，并检查浏览器连接状态是否显示 Agent API connected。不要只启动 5173 前端。

## 8. 已经踩过的坑：不要重复

1. **不要把 404 当成后端挂了。** Flask Demo 根路径没有页面，API 路由正常即可。
2. **不要混淆两个前端。** `frontend/` 是被测 Demo，`platform-frontend/` 是测试工作台。
3. **不要重复启动 Agent API。** 5001 出现 `Address already in use` 说明已有进程运行；先复用或停止旧进程。
4. **Network Error 先查服务和端口。** 5173 正常不代表 5001 Agent API 正常，也不代表 5000 被测 API 正常。
5. **PRD 和 API 合约缺一不可。** PRD 描述业务规则；target config 描述如何调用接口。只有 PRD 没有可调用 endpoint，无法执行 API 测试。
6. **两个 endpoint 要一起配置。** 只配置 `/api/register` 会导致登录用例缺失；登录注册样例需要 register 和 login 都在 `endpoints` 数组里。
7. **成功注册用例要避免用户名冲突。** SQLite 中重复用户名会返回 `Username already exists`，随机用户名或隔离测试数据可以避免误判。
8. **不要把失败用例当成 Agent 失败。** 当前 TC-REGISTER-002 失败是预埋 Bug 被发现的正确结果。
9. **不要让 LLM 决定 PASS/FAIL。** Expected/Actual 比较必须由程序完成，报告统计也必须来自执行记录。
10. **不要假设 LLM 永远返回合法 JSON。** 继续保留 Markdown fence 清理、结构校验和错误提示。
11. **不要提交密钥和运行目录。** 尤其是 `ai-agent/.env`、`venv/`、`node_modules/`、`users.db`、缓存和构建产物。
12. **不要覆盖样例 PRD。** `docs/PRD.md` 是活动文件，上传新 PRD 会替换它；长期应把样例放在 `docs/samples/` 并实现项目隔离。
13. **不要把 LibreSSL warning 当成主错误。** 先看最后一行 traceback；该警告此前没有阻止流程运行，后续可再升级 Python 环境。
14. **不要盲目覆盖 VS Code 的外部修改。** 出现 save conflict 时先比较编辑器版本和磁盘版本，再合并保留正确内容。
15. **不要在没有基线数据时编造效率提升。** 若要写效率指标，必须用同一份 PRD 做人工流程与 Agent 流程的多次计时对比。

## 9. 新会话开始时先做什么

新会话应先阅读本文件，然后执行只读检查：

```bash
cd /Users/peipe/Desktop/AI-Testing-Agent
find . -maxdepth 2 -type f \
  -not -path './ai-agent/venv/*' \
  -not -path './backend/venv/*' \
  -not -path './frontend/node_modules/*' \
  -not -path './platform-frontend/node_modules/*' \
  | sort
```

接着确认：

1. 活动目录是否仍是 `/Users/peipe/Desktop/AI-Testing-Agent`。
2. 是否有三个服务已经运行，避免重复启动。
3. `ai-agent/outputs/` 当前是否保留最近一次产物。
4. 需要修改代码时，先确认不是在旧 Git clone 上操作。
5. 任何涉及 GitHub 的操作前，先检查密钥、数据库、虚拟环境和构建目录是否会被提交。

当前最合理的下一项编码任务是：先完成根目录可复现配置和 Git 安全整理；如果只继续做产品功能，则优先实现 `project_id/run_id` 运行隔离，然后再考虑 OpenAPI 和 Playwright。
