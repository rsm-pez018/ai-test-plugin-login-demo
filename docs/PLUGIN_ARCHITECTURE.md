# AI 自动化测试插件原型架构方案

## 1. 文档目的

本文档描述 AI 驱动自动化测试插件的最小可验证原型，包括系统模块、数据流、职责边界和后续扩展方向。

当前原型使用 React + Flask 登录注册系统作为被测系统，验证从 PRD 分析到自动生成 Bug Report 的完整流程。

## 2. 产品目标

插件接收产品需求文档和被测系统的 API 合约，自动完成：

```text
上传 PRD
→ 需求结构化
→ 测试用例生成
→ 测试用例校验
→ API 执行
→ Expected / Actual 对比
→ Bug Report 生成
→ Test Report 生成
```

插件的定位是辅助测试工程师提高需求分析、用例设计和执行效率，不替代测试工程师的最终判断。

## 3. 当前 MVP 范围

### 已支持

- Markdown 和 TXT 格式 PRD 上传
- LLM 需求提取
- LLM API 测试用例生成
- 测试用例结构和 API 合约校验
- HTTP API 自动执行
- 状态码和响应消息确定性比对
- 失败用例分析
- Bug Report 和 Test Report 生成
- React + Ant Design 测试工作台

### 当前限制

- 主要验证 API 测试，不支持浏览器自动化
- PRD 上传和输出文件使用单项目全局路径
- API 合约需要手动配置，暂未支持 OpenAPI 导入
- Demo 使用 SQLite，密码明文存储，仅适用于本地原型
- Bug Report 暂未连接 Jira 或 GitHub Issues

## 4. 系统架构

```text
┌──────────────────────────────┐
│       Platform Frontend       │
│  PRD 上传、配置、执行、报告展示 │
│          React + Ant Design   │
└──────────────┬───────────────┘
               │ HTTP
               ▼
┌──────────────────────────────┐
│          Agent API            │
│           Flask :5001         │
│  接收请求并编排测试流程         │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│       Agent Orchestrator      │
│          run_agent.py         │
└──────┬───────┬───────┬───────┘
       │       │       │
       ▼       ▼       ▼
   LLM 模块  校验模块  执行模块
       │       │       │
       └───────┴───────┘
               ▼
┌──────────────────────────────┐
│       Demo System Under Test  │
│          Flask :5000          │
└──────────────────────────────┘
```

## 5. 核心模块职责

| 模块 | 类型 | 职责 | 主要输出 |
|---|---|---|---|
| Requirement Analyzer | LLM | 从 PRD 提取业务规则和预期行为 | `requirements.json` |
| Test Case Generator | LLM + 程序 | 根据需求和 API 合约生成测试用例及运行数据 | `test_cases.json` |
| Test Case Validator | 确定性程序 | 检查字段、接口、请求参数和成功用例覆盖 | 校验后的测试用例 |
| Test Executor | 确定性程序 | 调用目标 API 并记录响应 | `test_execution.json` |
| Result Analyzer | 确定性程序 | 比较 Expected 和 Actual，计算 PASS/FAIL | `result_analysis.json` |
| Bug Report Generator | 确定性模板 | 根据失败执行记录生成 Bug 单 | `bug_report.md` |
| Test Report Generator | 确定性模板 | 根据执行记录生成统计和测试报告 | `test_report.md` |

## 6. LLM 与确定性程序的边界

### LLM 负责

- 理解自然语言 PRD
- 提取业务规则
- 设计测试场景
- 生成结构化测试用例草稿
- 组织可读的说明文字

### 程序负责

- 校验 LLM 输出结构
- 校验接口和请求字段
- 生成唯一测试数据
- 调用真实 API
- 比较 Expected 和 Actual
- 计算通过数和失败数
- 生成报告中的事实字段

PASS/FAIL 不能交给 LLM 判断。报告中的测试数据、Expected、Actual 和统计数字必须来自真实执行记录，避免报告模型修改或编造事实。

## 7. 数据流和产物

### 输入

1. PRD：描述业务规则和预期行为。
2. API 合约：描述 base URL、接口、请求字段和预期响应。
3. 环境配置：包括目标环境和必要的认证信息。

### 中间数据

```text
requirements.json
→ test_cases.json
→ test_execution.json
→ result_analysis.json
```

### 最终产物

```text
bug_report.md
test_report.md
```

每次执行都应保留输入、测试用例、执行结果和报告，便于复盘和问题追踪。

## 8. 测试数据和前置依赖

测试数据可以由程序在每次运行开始时生成，不要求数据库预先存在真实数据。例如：

```text
valid_username
valid_password
short_username
non_existing_username
wrong_password
```

依赖其他数据的用例必须明确 setup 和执行顺序。例如登录测试需要先创建成功注册的用户，再使用相同账号登录。后续版本应将这些依赖显式建模为 fixture、setup 和 teardown，而不是仅依赖用例排序。

## 9. API 测试用例抽象

当前登录注册 Demo 使用用户名和密码。通用版本应抽象为操作、请求和断言：

```json
{
  "test_case_id": "TC-001",
  "operation_id": "create_order",
  "scenario": "Create order with empty items",
  "preconditions": [],
  "request": {
    "method": "POST",
    "path": "/orders",
    "body": {}
  },
  "expected": {
    "status_code": 400,
    "message": "Items are required"
  }
}
```

这样插件可以支持订单、支付、商品、内容和权限等不同 API 业务，而不依赖登录注册字段。

## 10. 后续演进路线

### Phase 1：完善 API 测试平台

- 引入 `project_id` 和 `run_id`
- 按项目和运行保存数据
- 支持 OpenAPI/Swagger 导入
- 支持认证、环境变量和多环境配置
- 完善 setup/teardown 和测试依赖
- 增加 JSON、Markdown 下载

### Phase 2：提升可靠性

- 使用严格的结构化 LLM 输出
- 增加超时、重试和错误恢复
- 增加人工审核和批准步骤
- 建立多 PRD、多 Bug 的评估集
- 统计覆盖率、Bug 召回率、误报率、延迟和成本

### Phase 3：扩展执行能力

- 增加 Playwright 浏览器执行器
- 增加 Jira/GitHub Issues 集成
- 增加权限、持久化和部署能力

## 11. 当前 Demo 验证结果

登录注册 Demo 的最新完整流程包含 10 个测试用例：

```text
总数：10
通过：9
失败：1
```

唯一失败用例验证了预埋业务 Bug：用户名少于 6 个字符时，注册 API 仍返回成功。

该结果证明原型已经完成从 PRD 分析、测试用例生成、API 执行到 Bug 和测试报告生成的最小闭环。
