const BASE_URL = '/api'

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
}

async function request<T = unknown>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options

  const config: RequestInit = { method, headers }
  if (body && method !== 'GET') {
    config.body = JSON.stringify(body)
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(`${BASE_URL}${path}`, config)
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json()
}

// 文件上传
export function uploadFile(file: File) {
  const form = new FormData()
  form.append('file', file)
  return fetch(`${BASE_URL}/upload`, { method: 'POST', body: form }).then(r => r.json())
}

// 分析模板
export function getTemplates() { return request('/templates') }

// 发起分析
export function runAnalysis(fileIds: string[], templateId: string, nlQuery?: string) {
  return request('/analysis/run', {
    method: 'POST',
    body: { file_ids: fileIds, template_id: templateId || null, nl_query: nlQuery || null },
  })
}

// 任务状态
export function getTask(taskId: string) { return request(`/tasks/${taskId}`) }

// 任务列表
export function getTasks() { return request('/tasks') }

// 获取报告
export function getReport(taskId: string) { return request(`/reports/${taskId}`) }

// 获取报告 HTML 内容
export async function getReportHtml(taskId: string): Promise<string> {
  const htmlRes = await fetch(`${BASE_URL}/reports/${taskId}`)
  if (!htmlRes.ok) throw new Error('报告获取失败')
  return htmlRes.text()
}

// 发送反馈
export function submitFeedback(taskId: string, satisfaction: string, missingItems: string[], description: string) {
  return request(`/feedback/${taskId}`, {
    method: 'POST',
    body: { satisfaction, missing_items: missingItems, description },
  })
}

// 知识库问答
export function askKnowledge(question: string, collection?: string, sessionId?: string) {
  return request('/knowledge/ask', {
    method: 'POST',
    body: { question, collection: collection || null, session_id: sessionId || null },
  })
}

// 获取知识库列表
export function getCollections() { return request('/knowledge/collections') }
