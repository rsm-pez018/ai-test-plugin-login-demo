import { useEffect, useMemo, useState } from 'react'
import {
  ApiOutlined,
  CheckCircleFilled,
  CloudUploadOutlined,
  FileSearchOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  ReloadOutlined,
  SettingOutlined,
  ThunderboltFilled,
  WarningFilled,
} from '@ant-design/icons'
import {
  Alert,
  Button,
  ConfigProvider,
  Divider,
  Empty,
  Form,
  Input,
  message,
  Select,
  Space,
  Spin,
  Statistic,
  Table,
  Tabs,
  Tag,
  Upload,
} from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { agentApi, getApiError } from './api'
import './App.css'

const { Dragger } = Upload

const demoEndpoints = [
  {
    name: 'Register',
    path: '/api/register',
    method: 'POST',
    request_body: { username: '{{username}}', password: '{{password}}' },
    expected_responses: [
      { condition: 'Valid username and password', status_code: 200, message: 'Registration_successful' },
      { condition: 'Empty username', status_code: 400, message: 'Username is required' },
      { condition: 'Username shorter than 6 characters', status_code: 400, message: 'Username length must be at least 6 characters' },
      { condition: 'Empty password', status_code: 400, message: 'Password is required' },
      { condition: 'Password shorter than 6 characters', status_code: 400, message: 'Password length must be at least 6 characters' },
    ],
  },
  {
    name: 'Login',
    path: '/api/login',
    method: 'POST',
    request_body: { username: '{{username}}', password: '{{password}}' },
    expected_responses: [
      { condition: 'Valid username and password', status_code: 200, message: 'Login successful' },
      { condition: 'Empty username', status_code: 400, message: 'Username is required' },
      { condition: 'Empty password', status_code: 400, message: 'Password is required' },
      { condition: 'Username does not exist', status_code: 400, message: 'Invalid username or password' },
      { condition: 'Incorrect password', status_code: 400, message: 'Invalid username or password' },
    ],
  },
]

const cloneDemoEndpoints = () => JSON.parse(JSON.stringify(demoEndpoints))
const RESULTS_STORAGE_KEY = 'ai-testing-workspace-results'
const ACTIVE_RESULT_STORAGE_KEY = 'ai-testing-workspace-active-result'

function EndpointEditor({ endpoint, index, onChange, onRemove }) {
  const update = (key, value) => onChange(index, { ...endpoint, [key]: value })

  const updateJson = (key, value) => {
    try {
      update(key, JSON.parse(value))
    } catch {
      update(`${key}_draft`, value)
    }
  }

  const requestValue = endpoint.request_body_draft ?? JSON.stringify(endpoint.request_body, null, 2)
  const responseValue = endpoint.expected_responses_draft ?? JSON.stringify(endpoint.expected_responses, null, 2)

  return (
    <div className="endpoint-editor">
      <div className="endpoint-heading">
        <Space size={8} wrap>
          <Tag color={endpoint.method === 'GET' ? 'blue' : 'green'}>{endpoint.method}</Tag>
          <strong>{endpoint.name || `Endpoint ${index + 1}`}</strong>
          <code>{endpoint.path || '/'}</code>
        </Space>
        <Button danger type="text" onClick={() => onRemove(index)}>Remove</Button>
      </div>
      <div className="endpoint-fields">
        <Input value={endpoint.name} placeholder="Endpoint name" onChange={(event) => update('name', event.target.value)} />
        <Select value={endpoint.method} onChange={(value) => update('method', value)} options={[{ value: 'GET' }, { value: 'POST' }, { value: 'PUT' }, { value: 'DELETE' }]} />
        <Input value={endpoint.path} placeholder="/api/example" onChange={(event) => update('path', event.target.value)} />
      </div>
      <div className="json-grid">
        <label>
          <span>Request body (JSON)</span>
          <Input.TextArea rows={6} value={requestValue} onChange={(event) => updateJson('request_body', event.target.value)} />
        </label>
        <label>
          <span>Expected responses (JSON)</span>
          <Input.TextArea rows={6} value={responseValue} onChange={(event) => updateJson('expected_responses', event.target.value)} />
        </label>
      </div>
    </div>
  )
}

function JsonView({ value }) {
  if (value === undefined || value === null) return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No output yet" />
  return <pre className="json-output">{JSON.stringify(value, null, 2)}</pre>
}

function App() {
  const [messageApi, contextHolder] = message.useMessage()
  const [connected, setConnected] = useState(false)
  const [checking, setChecking] = useState(true)
  const [busy, setBusy] = useState('')
  const [prdFile, setPrdFile] = useState(null)
  const [projectName, setProjectName] = useState('Login/Register Demo')
  const [baseUrl, setBaseUrl] = useState('http://127.0.0.1:5000')
  const [endpoints, setEndpoints] = useState(cloneDemoEndpoints)
  const [activeResult, setActiveResult] = useState(() => {
    try {
      return window.localStorage.getItem(ACTIVE_RESULT_STORAGE_KEY) || 'requirements'
    } catch {
      return 'requirements'
    }
  })
  const [results, setResults] = useState(() => {
    try {
      const storedResults = window.localStorage.getItem(RESULTS_STORAGE_KEY)
      return storedResults ? JSON.parse(storedResults) : {}
    } catch {
      return {}
    }
  })

  const checkHealth = async () => {
    setChecking(true)
    try {
      await agentApi.health()
      setConnected(true)
    } catch {
      setConnected(false)
    } finally {
      setChecking(false)
    }
  }

  useEffect(() => { checkHealth() }, [])

  useEffect(() => {
    try {
      if (Object.keys(results).length) {
        window.localStorage.setItem(RESULTS_STORAGE_KEY, JSON.stringify(results))
      }
      window.localStorage.setItem(ACTIVE_RESULT_STORAGE_KEY, activeResult)
    } catch {
      // Results remain available for the current session if browser storage is unavailable.
    }
  }, [results, activeResult])

  const validEndpoints = () => {
    const invalidJson = endpoints.some((endpoint) => endpoint.request_body_draft || endpoint.expected_responses_draft)
    if (invalidJson) throw new Error('Fix invalid JSON in the endpoint configuration first.')
    if (!endpoints.length) throw new Error('Add at least one endpoint.')
    return endpoints.map(({ request_body_draft, expected_responses_draft, ...endpoint }) => endpoint)
  }

  const runAction = async (name, action, onSuccess) => {
    setBusy(name)
    try {
      const response = await action()
      onSuccess?.(response)
      messageApi.success(`${name} completed`)
      return response
    } catch (error) {
      messageApi.error(getApiError(error))
      return null
    } finally {
      setBusy('')
    }
  }

  const uploadPrd = () => {
    if (!prdFile) return messageApi.warning('Choose a Markdown or text PRD first.')
    return runAction('PRD upload', () => agentApi.uploadPrd(prdFile, projectName), (response) => {
      setResults((current) => ({ ...current, upload: response }))
    })
  }

  const saveConfig = async () => {
    try {
      const config = { project_name: projectName, base_url: baseUrl, endpoints: validEndpoints() }
      return runAction('Target configuration', () => agentApi.configureTarget(config), (response) => {
        setResults((current) => ({ ...current, configuration: response }))
      })
    } catch (error) {
      messageApi.error(error.message)
      return null
    }
  }

  const analyze = () => runAction('Requirement analysis', agentApi.analyzeRequirements, (response) => {
    setResults((current) => ({ ...current, requirements: response.data ?? response.requirements ?? response }))
    setActiveResult('requirements')
  })

  const generate = () => runAction('Test case generation', agentApi.generateTestCases, (response) => {
    setResults((current) => ({ ...current, testCases: response.data ?? response.test_cases ?? response }))
    setActiveResult('testCases')
  })

  const execute = () => runAction('Test execution', agentApi.executeTests, (response) => {
    setResults((current) => ({ ...current, execution: response.data ?? response.execution_results ?? response }))
    setActiveResult('execution')
  })

  const reports = () => runAction('Report generation', agentApi.generateReports, (response) => {
    const payload = response.data ?? response
    const [analysis, bugReport, testReport] = Array.isArray(payload) ? payload : [payload.analysis, payload.bug_report, payload.test_report]
    setResults((current) => ({ ...current, analysis, bugReport, testReport }))
    setActiveResult('testReport')
  })

  const runAll = async () => {
    setBusy('Full agent run')
    try {
      if (prdFile) await agentApi.uploadPrd(prdFile, projectName)
      await agentApi.configureTarget({ project_name: projectName, base_url: baseUrl, endpoints: validEndpoints() })
      const response = await agentApi.runAll()
      const payload = response.data ?? response
      setResults({
        requirements: payload.requirements,
        testCases: payload.test_cases,
        execution: payload.execution_results,
        analysis: payload.analysis,
        bugReport: payload.bug_report,
        testReport: payload.test_report,
      })
      setActiveResult('testReport')
      messageApi.success('Full agent run completed')
    } catch (error) {
      messageApi.error(getApiError(error))
    } finally {
      setBusy('')
    }
  }

  const analysis = results.analysis || {}
  const execution = Array.isArray(results.execution) ? results.execution : []
  const failedCases = Array.isArray(analysis.failed_cases) ? analysis.failed_cases : []
  const passed = analysis.passed ?? execution.filter((item) => item.status === 'PASS').length
  const failed = analysis.failed ?? execution.filter((item) => item.status === 'FAIL').length
  const metrics = {
    requirements: Array.isArray(results.requirements) ? results.requirements.length : 0,
    testCases: Array.isArray(results.testCases) ? results.testCases.length : 0,
    passed,
    failed,
  }

  const requirements = Array.isArray(results.requirements) ? results.requirements : []
  const testCases = Array.isArray(results.testCases) ? results.testCases : []

  const requirementColumns = [
    { title: 'ID', dataIndex: 'requirement_id', key: 'requirement_id', width: 170 },
    { title: 'Module', dataIndex: 'module', key: 'module', width: 140 },
    { title: 'Field', dataIndex: 'field', key: 'field', width: 120 },
    { title: 'Rule', dataIndex: 'rule', key: 'rule', width: 220 },
    { title: 'Expected behavior', dataIndex: 'expected_behavior', key: 'expected_behavior' },
  ]

  const testCaseColumns = [
    { title: 'ID', dataIndex: 'test_case_id', key: 'test_case_id', width: 150 },
    { title: 'Scenario', dataIndex: 'scenario', key: 'scenario', width: 280 },
    {
      title: 'Endpoint',
      dataIndex: 'endpoint',
      key: 'endpoint',
      width: 180,
      render: (endpoint, record) => (
        <Space size={6}>
          <Tag color="blue">{record.method}</Tag>
          <code>{endpoint}</code>
        </Space>
      ),
    },
    {
      title: 'Test data',
      dataIndex: 'test_data',
      key: 'test_data',
      width: 240,
      render: (value) => <pre className="table-json">{JSON.stringify(value, null, 2)}</pre>,
    },
    {
      title: 'Expected',
      key: 'expected',
      width: 250,
      render: (_, record) => (
        <div>
          <div>HTTP {record.expected_status_code}</div>
          <div>{record.expected_message}</div>
        </div>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 110,
      render: (priority) => <Tag color={priority === 'Highest' ? 'red' : 'orange'}>{priority}</Tag>,
    },
  ]

  const requirementsView = requirements.length ? (
    <Table
      size="small"
      rowKey="requirement_id"
      columns={requirementColumns}
      dataSource={requirements}
      pagination={false}
      scroll={{ x: 1000 }}
      expandable={{ expandedRowRender: (record) => <JsonView value={record} /> }}
    />
  ) : <JsonView value={results.requirements} />

  const testCasesView = testCases.length ? (
    <Table
      size="small"
      rowKey="test_case_id"
      columns={testCaseColumns}
      dataSource={testCases}
      pagination={{ pageSize: 10 }}
      scroll={{ x: 1200 }}
      expandable={{ expandedRowRender: (record) => <JsonView value={record} /> }}
    />
  ) : <JsonView value={results.testCases} />

  const analysisColumns = [
    { title: 'Test case', dataIndex: 'test_case_id', key: 'test_case_id', width: 170 },
    { title: 'Scenario', dataIndex: 'scenario', key: 'scenario', width: 300 },
    {
      title: 'Expected',
      key: 'expected',
      width: 230,
      render: (_, record) => <div>HTTP {record.expected_status_code}<br />{record.expected_message}</div>,
    },
    {
      title: 'Actual',
      key: 'actual',
      width: 230,
      render: (_, record) => <div>HTTP {record.actual_status_code}<br />{record.actual_message}</div>,
    },
    { title: 'Reason', dataIndex: 'failure_reason', key: 'failure_reason' },
  ]

  const analysisView = results.analysis ? (
    <div className="analysis-output">
      <div className="analysis-summary">
        <div><span>Total</span><strong>{analysis.total ?? 0}</strong></div>
        <div className="analysis-passed"><span>Passed</span><strong>{analysis.passed ?? 0}</strong></div>
        <div className="analysis-failed"><span>Failed</span><strong>{analysis.failed ?? 0}</strong></div>
      </div>
      {failedCases.length ? (
        <Table
          size="small"
          rowKey="test_case_id"
          columns={analysisColumns}
          dataSource={failedCases}
          pagination={false}
          scroll={{ x: 1100 }}
          expandable={{ expandedRowRender: (record) => <JsonView value={record} /> }}
        />
      ) : (
        <Alert type="success" showIcon message="All executed test cases passed." />
      )}
    </div>
  ) : <JsonView value={results.analysis} />

  const executionColumns = [
    { title: 'Test case', dataIndex: 'test_case_id', key: 'test_case_id', width: 150 },
    { title: 'Scenario', dataIndex: 'scenario', key: 'scenario' },
    { title: 'Expected', dataIndex: 'expected_status_code', key: 'expected_status_code', width: 90 },
    { title: 'Actual', dataIndex: 'actual_status_code', key: 'actual_status_code', width: 90 },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 90, render: (status) => <Tag color={status === 'PASS' ? 'green' : 'red'}>{status}</Tag> },
  ]

  const resultTabs = useMemo(() => [
    { key: 'requirements', label: 'Requirements', children: requirementsView },
    { key: 'testCases', label: 'Test cases', children: testCasesView },
    { key: 'execution', label: 'Execution', children: execution.length ? <Table size="small" rowKey={(row, index) => row.test_case_id || index} columns={executionColumns} dataSource={execution} pagination={false} scroll={{ x: 760 }} /> : <JsonView value={results.execution} /> },
    { key: 'analysis', label: 'Analysis', children: analysisView },
    { key: 'bugReport', label: 'Bug report', children: results.bugReport ? <div className="markdown-output"><ReactMarkdown remarkPlugins={[remarkGfm]}>{results.bugReport}</ReactMarkdown></div> : <JsonView /> },
    { key: 'testReport', label: 'Test report', children: results.testReport ? <div className="markdown-output"><ReactMarkdown remarkPlugins={[remarkGfm]}>{results.testReport}</ReactMarkdown></div> : <JsonView /> },
  ], [results, execution, requirementsView, testCasesView, analysisView])

  const updateEndpoint = (index, value) => setEndpoints((current) => current.map((endpoint, endpointIndex) => endpointIndex === index ? value : endpoint))
  const removeEndpoint = (index) => setEndpoints((current) => current.filter((_, endpointIndex) => endpointIndex !== index))
  const addEndpoint = () => setEndpoints((current) => [...current, { name: 'New endpoint', path: '/api/', method: 'POST', request_body: {}, expected_responses: [] }])

  return (
    <ConfigProvider theme={{ token: { colorPrimary: '#1677ff', borderRadius: 6, colorBgLayout: '#f5f7fa', fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif' } }}>
      {contextHolder}
      <div className="app-shell">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark"><ThunderboltFilled /></div>
            <div><h1>AI Testing Workspace</h1><p>PRD to executable API tests</p></div>
          </div>
          <Space>
            <Tag icon={connected ? <CheckCircleFilled /> : <WarningFilled />} color={connected ? 'success' : 'error'}>
              {checking ? 'Checking API' : connected ? 'Agent API connected' : 'Agent API offline'}
            </Tag>
            <Button icon={<ReloadOutlined />} aria-label="Check Agent API" title="Check Agent API" onClick={checkHealth} loading={checking} />
          </Space>
        </header>

        <main className="workspace">
          {!connected && !checking && <Alert type="warning" showIcon message="Agent API is not available" description="Start agent_api.py on http://127.0.0.1:5001, then check the connection again." />}

          <section className="panel setup-panel">
            <div className="section-heading"><div><span className="eyebrow">Setup</span><h2>Project input</h2></div><Tag>{endpoints.length} endpoints</Tag></div>
            <div className="setup-grid">
              <div>
                <h3>1. Product requirement</h3>
                <Dragger accept=".md,.txt" maxCount={1} beforeUpload={(file) => { setPrdFile(file); return false }} onRemove={() => setPrdFile(null)} fileList={prdFile ? [prdFile] : []}>
                  <p className="ant-upload-drag-icon"><CloudUploadOutlined /></p>
                  <p className="ant-upload-text">Drop a PRD here or choose a file</p>
                  <p className="ant-upload-hint">Markdown and text files are supported.</p>
                </Dragger>
                <Button className="block-action" icon={<CloudUploadOutlined />} onClick={uploadPrd} loading={busy === 'PRD upload'} disabled={!prdFile}>Upload PRD</Button>
              </div>
              <div>
                <h3>2. System under test</h3>
                <Form layout="vertical">
                  <Form.Item label="Project name"><Input value={projectName} onChange={(event) => setProjectName(event.target.value)} /></Form.Item>
                  <Form.Item label="API base URL"><Input prefix={<ApiOutlined />} value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} /></Form.Item>
                </Form>
                <Space wrap>
                  <Button icon={<SettingOutlined />} onClick={saveConfig} loading={busy === 'Target configuration'}>Save configuration</Button>
                  <Button onClick={() => setEndpoints(cloneDemoEndpoints())}>Load Demo endpoints</Button>
                </Space>
              </div>
            </div>

            <Divider />
            <div className="subheading"><div><h3>API contract</h3><p>The contract tells the Agent how to call and evaluate the target system.</p></div><Button icon={<PlusOutlined />} onClick={addEndpoint}>Add endpoint</Button></div>
            <div className="endpoint-list">
              {endpoints.map((endpoint, index) => <EndpointEditor key={`${index}-${endpoint.name}`} endpoint={endpoint} index={index} onChange={updateEndpoint} onRemove={removeEndpoint} />)}
            </div>
          </section>

          <section className="panel workflow-panel">
            <div className="section-heading"><div><span className="eyebrow">Agent workflow</span><h2>Generate and execute</h2></div><Button type="primary" size="large" icon={<ThunderboltFilled />} onClick={runAll} loading={busy === 'Full agent run'}>Run full workflow</Button></div>
            <div className="workflow-grid">
              <Button icon={<FileSearchOutlined />} onClick={analyze} loading={busy === 'Requirement analysis'}>1. Analyze requirements</Button>
              <Button icon={<PlusOutlined />} onClick={generate} loading={busy === 'Test case generation'}>2. Generate test cases</Button>
              <Button icon={<PlayCircleOutlined />} onClick={execute} loading={busy === 'Test execution'}>3. Execute tests</Button>
              <Button icon={<FileSearchOutlined />} onClick={reports} loading={busy === 'Report generation'}>4. Generate reports</Button>
            </div>
          </section>

          <section className="results-band">
            <div className="metrics">
              <Statistic title="Requirements" value={metrics.requirements} />
              <Statistic title="Test cases" value={metrics.testCases} />
              <Statistic title="Passed" value={metrics.passed} valueStyle={{ color: '#16794b' }} />
              <Statistic title="Failed" value={metrics.failed} valueStyle={{ color: '#c9362b' }} />
            </div>
            <div className="panel result-panel">
              <div className="section-heading"><div><span className="eyebrow">Outputs</span><h2>Run results</h2></div>{busy && <Spin size="small" />}</div>
              <Tabs activeKey={activeResult} onChange={setActiveResult} items={resultTabs} />
            </div>
          </section>
        </main>
      </div>
    </ConfigProvider>
  )
}

export default App
