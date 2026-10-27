// API service layer for ERPNext Implementation Project Management

export function getCsrfToken() {
  return window.csrf_token || window.frappe?.csrf_token || ''
}

export async function request(method, endpoint, data = null) {
  let url = endpoint.startsWith('/') ? endpoint : `/api/method/${endpoint}`
  const headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Frappe-CSRF-Token': getCsrfToken(),
  }

  const options = {
    method,
    headers,
  }

  if (data) {
    if (method === 'GET') {
      const query = new URLSearchParams(data).toString()
      url += (url.includes('?') ? '&' : '?') + query
    } else {
      options.body = JSON.stringify(data)
    }
  }

  const response = await fetch(url, options)
  const json = await response.json()

  if (!response.ok || json.exc) {
    const errorMsg = json._server_messages
      ? JSON.parse(json._server_messages).join('\n')
      : (json.message || response.statusText || 'Unknown Server Error')
    console.error('API Error:', errorMsg, json)
    throw new Error(errorMsg)
  }

  return json.message !== undefined ? json.message : json
}

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------
export async function getProjects(filters = {}) {
  return request('POST', 'projects.api.project.get_projects', filters)
}

export async function getProject(projectName) {
  return request('POST', 'projects.api.project.get_project', { project_name: projectName })
}

export async function createProject(data) {
  return request('POST', 'projects.api.project.create_project', { data })
}

export async function updateProject(projectName, data) {
  return request('POST', 'projects.api.project.update_project', { project_name: projectName, data })
}

export async function deleteProject(projectName) {
  return request('POST', 'projects.api.project.delete_project', { project_name: projectName })
}

export async function addModuleToProject(projectName, moduleCode) {
  return request('POST', 'projects.api.project.add_module_to_project', { project_name: projectName, module_code: moduleCode })
}

// ---------------------------------------------------------------------------
// Tasks
// ---------------------------------------------------------------------------
export async function getTasks(filters = {}) {
  return request('POST', 'projects.api.task.get_tasks', filters)
}

export async function getTask(taskId) {
  return request('POST', 'projects.api.task.get_task', { task_id: taskId })
}

export async function createTask(data) {
  return request('POST', 'projects.api.task.create_task', { data })
}

export async function updateTask(taskId, data) {
  return request('POST', 'projects.api.task.update_task', { task_id: taskId, data })
}

export async function quickUpdateStatus(taskId, status) {
  return request('POST', 'projects.api.task.quick_update_status', { task_id: taskId, status })
}

export async function addTaskComment(taskId, content) {
  return request('POST', 'projects.api.task.add_comment', { task_id: taskId, content })
}

export async function sendTaskEmail(taskId, recipients, subject, message) {
  return request('POST', 'projects.api.task.send_task_email', {
    task_id: taskId,
    recipients,
    subject,
    message,
  })
}

export async function assignTask(taskId, userEmail, action = 'add') {
  return request('POST', 'projects.api.task.assign_task', {
    task_id: taskId,
    user_email: userEmail,
    action,
  })
}

// ---------------------------------------------------------------------------
// Dashboard & Calendar
// ---------------------------------------------------------------------------
export async function getPortfolioDashboard() {
  return request('POST', 'projects.api.dashboard.get_portfolio_dashboard')
}

export async function getCalendarEvents(filters = {}) {
  return request('POST', 'projects.api.dashboard.get_calendar_events', filters)
}

// ---------------------------------------------------------------------------
// Implementation Modules & Templates
// ---------------------------------------------------------------------------
export async function getImplementationModules() {
  return request('POST', 'projects.api.module.get_implementation_modules')
}

export async function saveModuleTemplate(moduleCode, data) {
  return request('POST', 'projects.api.module.save_module_template', {
    module_code: moduleCode,
    data,
  })
}

export async function createImplementationModule(data) {
  return request('POST', 'projects.api.module.create_implementation_module', data)
}

export async function deleteImplementationModule(moduleCode) {
  return request('POST', 'projects.api.module.delete_implementation_module', {
    module_code: moduleCode,
  })
}

// ---------------------------------------------------------------------------
// Notifications & Command Palette Search
// ---------------------------------------------------------------------------
export async function getNotifications(limit = 30) {
  return request('POST', 'projects.api.task.get_notifications', { limit })
}

export async function markNotificationRead(notificationId) {
  return request('POST', 'projects.api.task.mark_notification_read', { notification_id: notificationId })
}

export async function markAllNotificationsRead() {
  return request('POST', 'projects.api.task.mark_all_notifications_read')
}

export async function globalSearch(query) {
  return request('POST', 'projects.api.task.global_search', { query })
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------
export async function getUsers() {
  const res = await request('POST', 'frappe.client.get_list', {
    doctype: 'User',
    filters: { enabled: 1, user_type: 'System User' },
    fields: ['name', 'full_name', 'user_image'],
    limit_page_length: 100,
  })
  return res || []
}
