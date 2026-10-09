import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_AGENT_API_URL || 'http://127.0.0.1:5001',
  timeout: 120000,
})

const data = (response) => response.data

export const agentApi = {
  health: () => client.get('/api/health').then(data),
  uploadPrd: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/api/project/upload-prd', formData).then(data)
  },
  configureTarget: (config) =>
    client.post('/api/project/configure-target', config).then(data),
  analyzeRequirements: () =>
    client.post('/api/agent/analyze-requirements').then(data),
  generateTestCases: () =>
    client.post('/api/agent/generate-test-cases').then(data),
  executeTests: () => client.post('/api/agent/execute-tests').then(data),
  generateReports: () =>
    client.post('/api/agent/generate-reports').then(data),
  runAll: () => client.post('/api/agent/run-all').then(data),
}

export function getApiError(error) {
  return (
    error.response?.data?.message ||
    error.response?.data?.error ||
    error.message ||
    'Request failed'
  )
}
