<template>
  <div class="project-page">
    <header class="topbar">
      <div class="breadcrumb" aria-label="Breadcrumb">
        <router-link to="/projects">Projects</router-link>
        <Icon name="chevron-right" :size="13" />
        <strong>{{ project.project_name || projectName }}</strong>
      </div>
      <div class="topbar-actions">
        <label class="global-search">
          <Icon name="search" :size="15" />
          <input
            v-model="taskQuery"
            type="search"
            placeholder="Search projects, tasks..."
            aria-label="Search projects and tasks"
            @focus="projectView = 'Work plan'"
          />
          <kbd>⌘ K</kbd>
        </label>
        <button type="button" class="icon-button notification-button" aria-label="Notifications" @click="$emit('open-notifications')">
          <Icon name="bell" :size="16" />
        </button>
        <button type="button" class="icon-button" aria-label="Search" @click="$emit('open-search')">
          <Icon name="search" :size="16" />
        </button>
      </div>
    </header>

    <div v-if="loading" class="project-content">
      <p class="detail-empty">Loading project...</p>
    </div>
    <div v-else-if="!project.name" class="project-content">
      <p class="detail-empty">Project not found.</p>
    </div>

    <div v-else class="project-content">
      <section class="project-hero">
        <div class="project-heading">
          <div class="project-eyebrow">
            <span class="eyebrow-dot" />
            CLIENT IMPLEMENTATION
            <span class="eyebrow-separator">/</span>
            ERPNEXT
          </div>
          <div class="project-title-row">
            <h1>{{ project.project_name }}</h1>
            <span class="project-status" :class="{ 'is-risk': project.stats?.overdue_tasks }">
              <span />{{ project.stats?.overdue_tasks ? 'Needs attention' : 'On track' }}
            </span>
          </div>
          <p>ERPNext implementation · {{ stageLabel }}</p>
        </div>
        <div class="project-actions">
          <div v-if="teamPeople.length" class="team-stack">
            <span
              v-for="person in teamPeople.slice(0, 4)"
              :key="person.key"
              class="avatar avatar-small"
              :class="person.tone"
              :title="person.name"
            >{{ person.initials }}</span>
            <span v-if="teamPeople.length > 4" class="team-more">+{{ teamPeople.length - 4 }}</span>
          </div>
          <button type="button" class="share-button" @click="copyLink">
            <Icon name="share" :size="14" />
            {{ copied ? 'Copied' : 'Share' }}
          </button>
          <button type="button" class="primary-action" @click="startNewTask">
            <Icon name="plus" :size="14" />
            New task
          </button>
        </div>
      </section>

      <section class="project-health">
        <div class="health-progress-card">
          <div class="health-progress-topline">
            <span>Project completion</span>
            <strong>{{ project.stats?.percent_complete || 0 }}%</strong>
          </div>
          <div class="health-progress-track">
            <span :style="{ width: (project.stats?.percent_complete || 0) + '%' }" />
          </div>
          <div class="health-progress-foot">
            <span>{{ project.stats?.completed_tasks || 0 }} of {{ project.stats?.total_tasks || 0 }} tasks complete</span>
            <span v-if="!project.stats?.overdue_tasks" class="on-track-label">
              <Icon name="check-circle" :size="12" /> On track
            </span>
          </div>
        </div>
        <div class="health-divider" />
        <div class="health-stat">
          <span class="health-icon health-icon-alert"><Icon name="alert-circle" :size="16" /></span>
          <div>
            <strong>{{ String(project.stats?.overdue_tasks || 0).padStart(2, '0') }}</strong>
            <span>Overdue tasks</span>
          </div>
        </div>
        <div class="health-divider" />
        <div class="health-stat">
          <span class="health-icon health-icon-milestone"><Icon name="calendar" :size="16" /></span>
          <div>
            <strong>{{ goLiveLabel }}</strong>
            <span>{{ goLiveHint }}</span>
          </div>
        </div>
        <div class="phase-chip">
          <span>PHASE {{ phaseIndex }} / {{ stages.length }}</span>
          <select v-model="project.implementation_stage" @change="handleStageChange">
            <option v-for="stage in stages" :key="stage.value" :value="stage.value">{{ stage.label }}</option>
          </select>
        </div>
      </section>

      <nav class="project-tabs" aria-label="Project views">
        <button type="button" class="project-tab" :class="{ 'is-active': projectView === 'Work plan' }" @click="projectView = 'Work plan'">
          <Icon name="list-todo" :size="15" /> Work plan
        </button>
        <button type="button" class="project-tab" :class="{ 'is-active': projectView === 'Timeline' }" @click="projectView = 'Timeline'">
          <Icon name="calendar" :size="15" /> Timeline
        </button>
        <button type="button" class="project-tab" :class="{ 'is-active': projectView === 'Files' }" @click="projectView = 'Files'">
          <Icon name="file-text" :size="15" /> Files
        </button>
        <button type="button" class="project-tab" :class="{ 'is-active': projectView === 'Activity' }" @click="projectView = 'Activity'">
          <Icon name="activity" :size="15" /> Activity
        </button>
        <div class="tabs-spacer" />
        <span class="updated-label"><span />Live from ERPNext</span>
      </nav>

      <div v-if="projectView === 'Work plan'" class="workspace-grid">
        <section class="surface-panel workstream-panel">
          <div class="panel-heading">
            <div>
              <h2>Workstreams</h2>
              <p>ERPNext modules</p>
            </div>
            <button type="button" class="icon-button" aria-label="Add a module" @click="showAddModuleModal = true">
              <Icon name="more-horizontal" :size="16" />
            </button>
          </div>
          <button type="button" class="workstream-total" @click="selectModule('')">
            <span class="total-icon"><Icon name="layers" :size="12" /></span>
            <span>All workstreams</span>
            <strong>{{ project.tasks?.length || 0 }}</strong>
          </button>
          <div class="workstream-list">
            <button
              v-for="(mod, index) in project.modules || []"
              :key="mod.module"
              type="button"
              class="workstream-row"
              :class="{ 'is-selected': selectedModuleCode === mod.module }"
              @click="selectModule(mod.module)"
            >
              <span class="workstream-icon" :class="'workstream-icon-' + tone(index)">
                <Icon name="layers" :size="14" />
              </span>
              <span class="workstream-content">
                <span class="workstream-name-line">
                  <span class="workstream-name">{{ mod.module_title || mod.module_name || mod.module }}</span>
                  <span class="workstream-percent">{{ Math.round(mod.progress || 0) }}%</span>
                </span>
                <span class="workstream-progress-track">
                  <span :class="'progress-' + tone(index)" :style="{ width: (mod.progress || 0) + '%' }" />
                </span>
                <span class="workstream-meta">
                  {{ mod.completed_tasks || 0 }}/{{ mod.total_tasks || 0 }} tasks
                  <span v-if="mod.overdue_tasks" class="workstream-overdue">{{ mod.overdue_tasks }} overdue</span>
                </span>
              </span>
              <Icon name="chevron-right" class="workstream-chevron" :size="14" />
            </button>
          </div>
          <button type="button" class="add-workstream" @click="showAddModuleModal = true">
            <Icon name="plus" :size="14" />
            Add a workstream
          </button>
        </section>

        <section class="surface-panel task-list-panel">
          <div class="task-panel-heading">
            <div>
              <div class="panel-kicker">WORKSTREAM</div>
              <h2>{{ selectedModule?.title || 'All workstreams' }}</h2>
              <p>{{ moduleCompleted }} of {{ moduleTasks.length }} tasks complete</p>
            </div>
          </div>
          <div class="task-toolbar">
            <label class="task-search">
              <Icon name="search" :size="14" />
              <input v-model="taskQuery" type="search" placeholder="Filter tasks" aria-label="Filter tasks" />
            </label>
            <button type="button" class="filter-button" aria-label="Sort by due date" @click="sortDesc = !sortDesc">
              <Icon name="list-filter" :size="14" />
            </button>
          </div>
          <div class="task-filter-tabs">
            <button
              v-for="item in filterItems"
              :key="item.id"
              type="button"
              class="task-filter-tab"
              :class="{ 'is-active': taskFilter === item.id }"
              @click="taskFilter = item.id"
            >
              {{ item.label }}<span>{{ item.count }}</span>
            </button>
            <button type="button" class="sort-button" aria-label="Sort tasks" @click="sortDesc = !sortDesc">
              <Icon name="arrow-up-down" :size="14" />
            </button>
          </div>
          <div v-if="isAddingTask" class="quick-add-task">
            <input
              v-model="newTaskTitle"
              type="text"
              placeholder="Write a task title..."
              @keydown.enter.prevent="addQuickTask"
            />
            <button type="button" class="primary-action quick-add-submit" :disabled="!newTaskTitle.trim() || addingTask" @click="addQuickTask">Add</button>
            <button type="button" class="icon-button" @click="isAddingTask = false"><Icon name="x" :size="14" /></button>
          </div>
          <div class="task-list-scroll">
            <ul v-if="visibleTasks.length" class="task-list">
              <li v-for="task in visibleTasks" :key="task.name" class="task-row" :class="{ 'is-selected': task.name === taskId }">
                <button
                  type="button"
                  class="task-complete-button"
                  :class="{ 'is-complete': task.status === 'Completed' }"
                  @click="toggleComplete(task)"
                >
                  <Icon :name="task.status === 'Completed' ? 'check-circle' : 'circle'" :size="16" />
                </button>
                <button type="button" class="task-main" @click="goToTask(task)">
                  <span class="task-title-line">
                    <span class="task-title" :class="{ 'task-title-complete': task.status === 'Completed' }">{{ task.subject }}</span>
                    <span v-if="task.priority === 'High' || task.priority === 'Urgent'" class="priority-marker">
                      <Icon name="flag" :size="12" />
                    </span>
                  </span>
                  <span class="task-meta-line">
                    <span class="status-pill" :class="statusClass(task.status)"><span />{{ statusLabel(task.status) }}</span>
                    <span class="task-meta-dot">·</span>
                    <span :class="task.is_overdue && task.status !== 'Completed' ? 'due-overdue' : 'task-due'">
                      {{ task.is_overdue && task.status !== 'Completed' ? 'Overdue · ' : '' }}{{ formatDate(task.exp_end_date) || 'No date' }}
                    </span>
                  </span>
                </button>
                <span v-if="assigneeLabel(task)" class="task-assignee" :title="assigneeLabel(task)">
                  <span class="avatar avatar-small" :class="avatarTone(assigneeLabel(task))">{{ initials(assigneeLabel(task)) }}</span>
                </span>
                <span v-else class="task-unassigned"><Icon name="users" :size="14" /></span>
              </li>
            </ul>
            <div v-else class="task-empty-state">
              <span class="empty-icon"><Icon name="search" :size="16" /></span>
              <strong>No tasks found</strong>
              <p>Try another search or switch the filter.</p>
            </div>
          </div>
          <button v-if="!isAddingTask" type="button" class="task-add-row" @click="startNewTask">
            <Icon name="plus" :size="14" />
            Add a task
          </button>
        </section>

        <TaskTicketDetail
          v-if="taskId"
          :task-id="taskId"
          :project-label="project.project_name"
          :module-label="crumbModule?.title || ''"
          @updated="loadProject"
        />
        <section v-else class="surface-panel task-detail-panel detail-empty">
          <span class="empty-icon"><Icon name="list-todo" :size="16" /></span>
          <h2>Select a task</h2>
          <p>Choose a task from the workstream to see its details and activity.</p>
        </section>
      </div>

      <section v-else-if="projectView === 'Timeline'" class="surface-panel secondary-view timeline-view">
        <div class="secondary-view-heading">
          <div>
            <span class="panel-kicker">PROJECT SCHEDULE</span>
            <h2>Milestones and delivery plan</h2>
            <p>What this implementation is moving through next.</p>
          </div>
        </div>
        <div v-if="timelineRows.length" class="timeline-list">
          <article v-for="(row, index) in timelineRows" :key="row.key" class="milestone-row" :class="'milestone-' + row.tone">
            <div class="milestone-date">{{ row.date }}<span>{{ row.year }}</span></div>
            <div class="milestone-track">
              <span class="milestone-dot">
                <Icon v-if="row.tone === 'complete'" name="check" :size="12" />
              </span>
              <span v-if="index < timelineRows.length - 1" class="milestone-line" />
            </div>
            <div class="milestone-copy">
              <div class="milestone-title-row">
                <h3>{{ row.title }}</h3>
                <span class="milestone-status" :class="'milestone-status-' + row.tone">{{ row.status }}</span>
              </div>
              <p>{{ row.detail }}</p>
              <div class="milestone-progress"><span :style="{ width: row.progress + '%' }" /></div>
            </div>
          </article>
        </div>
        <div v-else class="detail-empty">
          <h2>No milestones yet</h2>
          <p>Mark a task as a milestone and it will show up on this plan.</p>
        </div>
      </section>

      <section v-else-if="projectView === 'Files'" class="surface-panel secondary-view files-view">
        <div class="secondary-view-heading">
          <div>
            <span class="panel-kicker">PROJECT LIBRARY</span>
            <h2>Project files</h2>
            <p>Files attached to this implementation and its tasks.</p>
          </div>
        </div>
        <div v-if="project.files?.length" class="file-grid">
          <a v-for="file in project.files" :key="file.name" class="project-file-card" :href="file.file_url" target="_blank">
            <div class="file-preview" :class="filePreviewClass(file.file_name)">
              <Icon :name="isSheet(file.file_name) ? 'file-text' : 'file-text'" :size="22" />
              <span>{{ fileKind(file.file_name) }}</span>
            </div>
            <div class="project-file-copy">
              <strong>{{ file.file_name }}</strong>
              <span>{{ file.task_subject || formatBytes(file.file_size) }}</span>
            </div>
            <div class="project-file-footer"><span>{{ formatDate(file.creation) }}</span></div>
          </a>
        </div>
        <div v-else class="detail-empty">
          <h2>No files yet</h2>
          <p>Attach a file on a task or a comment and it will be listed here.</p>
        </div>
      </section>

      <section v-else class="surface-panel secondary-view activity-view">
        <div class="secondary-view-heading">
          <div>
            <span class="panel-kicker">TEAM UPDATES</span>
            <h2>Project activity</h2>
            <p>Comments and messages across this implementation.</p>
          </div>
        </div>
        <div v-if="project.recent_activities?.length" class="activity-feed-list">
          <article v-for="event in project.recent_activities" :key="event.name" class="feed-event">
            <span class="avatar" :class="avatarTone(event.sender_name || event.sender)">{{ initials(event.sender_name || event.sender) }}</span>
            <div class="feed-event-copy">
              <p>
                <strong>{{ event.sender_name || event.sender || 'Someone' }}</strong>
                {{ event.activity_type === 'Communication' ? 'sent a message on' : 'commented on' }}
                <b>{{ taskSubject(event.task_name) }}</b>
              </p>
              <span>{{ plainText(event.content) }}</span>
            </div>
            <span class="feed-event-icon"><Icon name="message-square" :size="14" /></span>
          </article>
        </div>
        <div v-else class="detail-empty">
          <h2>No activity yet</h2>
          <p>Comments on tasks will show up here.</p>
        </div>
      </section>

      <footer class="project-footer">
        <span><Icon name="sparkles" :size="14" /> Project updates stay connected to your ERPNext rollout.</span>
        <span v-if="project.modified">Updated {{ formatDateTime(project.modified) }}</span>
      </footer>
    </div>

    <div v-if="showAddModuleModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl border border-outline-gray-2 p-5 max-w-md w-full space-y-3.5 shadow-2xl">
        <h3 class="text-sm font-semibold">Add a workstream</h3>
        <p class="text-xs text-ink-gray-5">Standard tasks for the module are created with it.</p>
        <select v-model="moduleToAdd" class="w-full px-3 py-2 text-xs border border-outline-gray-2 bg-white">
          <option value="">Choose a module</option>
          <option
            v-for="m in allModules"
            :key="m.module_code"
            :value="m.module_code"
            :disabled="project.modules?.some(pm => pm.module === m.module_code)"
          >
            {{ m.module_name }}
          </option>
        </select>
        <div class="flex justify-end gap-2 pt-2">
          <button type="button" class="share-button" @click="showAddModuleModal = false">Cancel</button>
          <button type="button" class="primary-action" :disabled="!moduleToAdd || addingModule" @click="handleAddModule">Add module</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import TaskTicketDetail from '../components/TaskTicketDetail.vue'
import {
  addModuleToProject,
  createTask,
  getImplementationModules,
  getProject,
  updateProject,
  updateTask,
} from '../api'

const props = defineProps({
  projectName: { type: String, required: true },
  taskId: { type: String, default: '' },
})

defineEmits(['open-new-task', 'open-search', 'open-notifications', 'select-task'])

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const project = ref({})
const showAddModuleModal = ref(false)
const moduleToAdd = ref('')
const addingModule = ref(false)
const allModules = ref([])
const projectView = ref('Work plan')
const taskFilter = ref('all')
const taskQuery = ref('')
const sortDesc = ref(false)
const isAddingTask = ref(false)
const newTaskTitle = ref('')
const addingTask = ref(false)
const copied = ref(false)

const stages = [
  { value: 'Discovery', label: 'Discovery & Planning' },
  { value: 'Design', label: 'Solution Design' },
  { value: 'Configuration & Customization', label: 'Configuration' },
  { value: 'Data Migration', label: 'Data Migration' },
  { value: 'UAT & Training', label: 'UAT & Training' },
  { value: 'Go-Live', label: 'Go-live readiness' },
  { value: 'Hypercare Support', label: 'Hypercare' },
  { value: 'Closed', label: 'Closed' },
]
const tones = ['violet', 'blue', 'teal', 'coral', 'amber', 'lilac', 'slate']
const avatarTones = ['avatar-indigo', 'avatar-coral', 'avatar-teal', 'avatar-lilac', 'avatar-amber']

const openTask = computed(() => {
  if (!props.taskId) return null
  return (project.value.tasks || []).find(task => task.name === props.taskId) || null
})

const selectedModuleCode = computed(() => {
  if (route.query.scope === 'all') return ''
  if (route.query.module) return String(route.query.module)
  if (props.taskId && openTask.value?.implementation_module) return openTask.value.implementation_module
  return project.value.modules?.[0]?.module || ''
})

const selectedModule = computed(() => {
  const code = selectedModuleCode.value
  if (!code) return null
  const mod = (project.value.modules || []).find(item => item.module === code)
  return {
    code,
    title: mod?.module_title || mod?.module_name || code,
  }
})

const crumbModule = computed(() => selectedModule.value)

const moduleTasks = computed(() => {
  const tasks = project.value.tasks || []
  if (!selectedModuleCode.value) return tasks
  return tasks.filter(task => task.implementation_module === selectedModuleCode.value)
})

const moduleCompleted = computed(() => moduleTasks.value.filter(task => task.status === 'Completed').length)

const filterItems = computed(() => {
  const tasks = moduleTasks.value
  return [
    { id: 'all', label: 'All', count: tasks.length },
    { id: 'open', label: 'Open', count: tasks.filter(task => task.status !== 'Completed' && task.status !== 'Cancelled').length },
    { id: 'overdue', label: 'Overdue', count: tasks.filter(task => task.is_overdue).length },
  ]
})

const visibleTasks = computed(() => {
  const query = taskQuery.value.trim().toLowerCase()
  const rows = moduleTasks.value.filter(task => {
    const matchesQuery = !query || `${task.subject} ${task.name}`.toLowerCase().includes(query)
    const matchesFilter = taskFilter.value === 'all'
      || (taskFilter.value === 'open' && task.status !== 'Completed' && task.status !== 'Cancelled')
      || (taskFilter.value === 'overdue' && task.is_overdue)
    return matchesQuery && matchesFilter
  })
  return [...rows].sort((a, b) => {
    const left = String(a.exp_end_date || '9999')
    const right = String(b.exp_end_date || '9999')
    return sortDesc.value ? right.localeCompare(left) : left.localeCompare(right)
  })
})

const stageLabel = computed(() => {
  const current = stages.find(stage => stage.value === project.value.implementation_stage)
  return current?.label || project.value.implementation_stage || 'Discovery & Planning'
})

const phaseIndex = computed(() => {
  const index = stages.findIndex(stage => stage.value === project.value.implementation_stage)
  return index >= 0 ? index + 1 : 1
})

const goLiveLabel = computed(() => formatDate(project.value.expected_end_date) || 'No date')

const goLiveHint = computed(() => {
  const days = daysUntil(project.value.expected_end_date)
  if (days === null) return 'Go-live target'
  if (days === 0) return 'Go-live target · today'
  if (days > 0) return `Go-live target · ${days} days`
  return `Go-live target · ${Math.abs(days)} days ago`
})

const teamPeople = computed(() => {
  const people = []
  const seen = new Set()
  const add = (name) => {
    const label = String(name || '').trim()
    if (!label || seen.has(label)) return
    seen.add(label)
    people.push({
      key: label,
      name: label.includes('@') ? label.split('@')[0] : label,
      initials: initials(label.includes('@') ? label.split('@')[0] : label),
      tone: avatarTone(label),
    })
  }
  add(project.value.project_manager_name)
  add(project.value.partner_poc_name)
  add(project.value.client_poc_name)
  for (const task of project.value.tasks || []) {
    for (const email of task.assignees || []) add(email)
  }
  return people
})

const timelineRows = computed(() => {
  const milestones = (project.value.tasks || []).filter(task => task.is_milestone)
  const source = milestones.length ? milestones : (project.value.modules || [])
  if (milestones.length) {
    return milestones.map(task => ({
      key: task.name,
      title: task.subject,
      detail: task.module_title || 'Milestone',
      date: formatDate(task.exp_end_date) || '—',
      year: yearOf(task.exp_end_date),
      status: statusLabel(task.status),
      tone: task.status === 'Completed' ? 'complete' : task.is_overdue ? 'target' : 'active',
      progress: task.status === 'Completed' ? 100 : Number(task.progress || 40),
    }))
  }
  return source.map(mod => ({
    key: mod.module,
    title: mod.module_title || mod.module_name || mod.module,
    detail: `${mod.completed_tasks || 0} of ${mod.total_tasks || 0} tasks`,
    date: 'Now',
    year: '',
    status: (mod.progress || 0) >= 100 ? 'Complete' : 'In progress',
    tone: (mod.progress || 0) >= 100 ? 'complete' : 'active',
    progress: mod.progress || 0,
  }))
})

onMounted(async () => {
  await loadProject()
  try {
    allModules.value = await getImplementationModules()
  } catch (e) {
    console.error(e)
  }
})

watch(() => props.projectName, () => {
  loadProject()
})

watch([() => props.taskId, () => (project.value.tasks || []).length], () => {
  if (props.taskId || !project.value.name) return
  const first = visibleTasks.value[0]
  if (first) goToTask(first)
})

async function loadProject() {
  loading.value = !project.value.name
  try {
    project.value = await getProject(props.projectName)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function selectModule(code) {
  const query = code ? { module: code } : { scope: 'all' }
  const tasks = (project.value.tasks || []).filter(task => !code || task.implementation_module === code)
  const first = tasks[0]
  if (first) {
    router.push({ path: `/projects/${props.projectName}/tasks/${first.name}`, query })
    return
  }
  router.push({ path: '/projects/' + props.projectName, query })
}

function goToTask(task) {
  router.push({
    path: `/projects/${props.projectName}/tasks/${task.name}`,
    query: task.implementation_module ? { module: task.implementation_module } : { scope: 'all' },
  })
}

function startNewTask() {
  projectView.value = 'Work plan'
  isAddingTask.value = true
  newTaskTitle.value = ''
}

async function addQuickTask() {
  const subject = newTaskTitle.value.trim()
  if (!subject) return
  addingTask.value = true
  try {
    const created = await createTask({
      subject,
      project: project.value.name,
      implementation_module: selectedModuleCode.value || undefined,
      status: 'Open',
    })
    newTaskTitle.value = ''
    isAddingTask.value = false
    await loadProject()
    const name = created?.name || created?.task_name
    if (name) {
      router.push({
        path: `/projects/${props.projectName}/tasks/${name}`,
        query: selectedModuleCode.value ? { module: selectedModuleCode.value } : {},
      })
    }
  } catch (e) {
    alert('Could not add the task')
  } finally {
    addingTask.value = false
  }
}

async function toggleComplete(task) {
  const status = task.status === 'Completed' ? 'Open' : 'Completed'
  try {
    await updateTask(task.name, { status, progress: status === 'Completed' ? 100 : task.progress || 0 })
    await loadProject()
  } catch (e) {
    alert('Could not update the task')
  }
}

async function handleStageChange() {
  try {
    await updateProject(project.value.name, { implementation_stage: project.value.implementation_stage })
  } catch (e) {
    alert('Could not update the stage')
  }
}

async function handleAddModule() {
  if (!moduleToAdd.value) return
  addingModule.value = true
  try {
    await addModuleToProject(project.value.name, moduleToAdd.value)
    showAddModuleModal.value = false
    moduleToAdd.value = ''
    await loadProject()
  } catch (e) {
    alert('Could not add the module')
  } finally {
    addingModule.value = false
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copied.value = true
    setTimeout(() => { copied.value = false }, 1600)
  } catch (e) {
    copied.value = false
  }
}

function assigneeLabel(task) {
  const first = (task.assignees || [])[0]
  if (!first) return ''
  return String(first).includes('@') ? String(first).split('@')[0] : String(first)
}

function taskSubject(name) {
  return (project.value.tasks || []).find(task => task.name === name)?.subject || name
}

function plainText(value) {
  const node = document.createElement('div')
  node.innerHTML = String(value || '')
  return (node.textContent || '').replace(/\s+/g, ' ').trim()
}

function tone(index) {
  return tones[index % tones.length]
}

function avatarTone(name) {
  let total = 0
  for (const char of String(name || '')) total += char.charCodeAt(0)
  return avatarTones[total % avatarTones.length]
}

function initials(name) {
  const parts = String(name || '?').trim().split(/[\s@._-]+/).filter(Boolean).slice(0, 2)
  return parts.map(part => part[0]?.toUpperCase() || '').join('') || '?'
}

function statusLabel(status) {
  if (status === 'Working') return 'In progress'
  if (status === 'Pending Review') return 'In review'
  if (status === 'Open') return 'To do'
  return status || 'To do'
}

function statusClass(status) {
  if (status === 'Completed') return 'status-completed'
  if (status === 'Working') return 'status-in-progress'
  if (status === 'Pending Review') return 'status-in-review'
  return 'status-to-do'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(String(dateStr).split(' ')[0])
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function yearOf(dateStr) {
  if (!dateStr) return ''
  const date = new Date(String(dateStr).split(' ')[0])
  return Number.isNaN(date.getTime()) ? '' : String(date.getFullYear())
}

function daysUntil(dateStr) {
  if (!dateStr) return null
  const date = new Date(String(dateStr).split(' ')[0])
  if (Number.isNaN(date.getTime())) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return Math.round((date.getTime() - today.getTime()) / 86400000)
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(String(dateStr).replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return String(dateStr)
  return date.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

function fileKind(name) {
  const ext = String(name || '').split('.').pop().toLowerCase()
  if (ext === 'xlsx' || ext === 'xls' || ext === 'csv') return 'XLSX'
  if (ext === 'pdf') return 'PDF'
  return (ext || 'FILE').slice(0, 4).toUpperCase()
}

function isSheet(name) {
  return ['xlsx', 'xls', 'csv'].includes(String(name || '').split('.').pop().toLowerCase())
}

function filePreviewClass(name) {
  return isSheet(name) ? 'file-preview-sheet' : 'file-preview-pdf'
}

function formatBytes(size) {
  const value = Number(size || 0)
  if (!value) return 'File'
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`
  return `${(value / (1024 * 1024)).toFixed(1)} MB`
}

defineExpose({ loadProject })
</script>
