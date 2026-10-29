<template>
  <div class="h-full flex flex-col overflow-hidden app-canvas">
    <div v-if="currentTaskId" class="h-full flex overflow-hidden min-w-0">
      <aside class="w-80 shrink-0 border-r border-outline-gray-1 bg-white flex flex-col min-h-0">
        <div class="h-12 px-3 border-b border-outline-gray-1 flex items-center justify-between shrink-0">
          <button
            type="button"
            class="text-sm font-semibold text-ink-gray-8 hover:text-ink-gray-9"
            @click="handleBackToList"
          >
            Tasks
          </button>
          <span class="text-[11px] text-ink-gray-4">{{ tasks.length }}</span>
        </div>
        <div class="flex-1 overflow-y-auto py-1">
          <button
            v-for="item in tasks"
            :key="item.name"
            type="button"
            class="w-full text-left px-3 py-2.5 border-l-2 transition"
            :class="item.name === currentTaskId
              ? 'bg-[#f4f7fb] border-[#1d6fe8]'
              : 'border-transparent hover:bg-surface-gray-1'"
            @click="handleSelectTask(item.name)"
          >
            <div class="flex items-start gap-2">
              <span
                class="mt-1 size-3.5 rounded-full border shrink-0"
                :class="item.status === 'Completed' ? 'bg-emerald-500 border-emerald-500' : 'border-ink-gray-4'"
              />
              <div class="min-w-0">
                <div
                  class="text-[13px] font-medium text-ink-gray-9 truncate"
                  :class="item.status === 'Completed' ? 'text-ink-gray-5' : ''"
                >
                  {{ item.subject }}
                </div>
                <div class="text-[11px] text-ink-gray-4 truncate mt-0.5">
                  {{ item.project_title || item.project || 'No project' }}
                  <span v-if="item.exp_end_date"> · {{ item.exp_end_date }}</span>
                </div>
              </div>
            </div>
          </button>
          <div v-if="!tasks.length" class="px-4 py-8 text-xs text-ink-gray-4 text-center">
            No tasks in this view.
          </div>
        </div>
      </aside>
      <TaskTicketDetail
        class="flex-1 min-w-0"
        :task-id="currentTaskId"
        :show-back="true"
        @back="handleBackToList"
        @updated="loadTasks"
      />
    </div>

    <!-- CASE 2: Tasks Explorer (List, Kanban, Calendar) -->
    <div v-show="!currentTaskId" class="h-full flex flex-col overflow-hidden">
      <!-- Layout Header matching Frappe Helpdesk Tickets.vue 1:1 -->
      <LayoutHeader>
        <template #left-header>
          <div class="flex items-center">
            <router-link
              to="/tasks"
              class="text-sm font-semibold text-ink-gray-5 hover:text-ink-gray-8 transition"
            >
              Tasks
            </router-link>
            <span class="mx-1 text-ink-gray-4">/</span>
            
            <!-- View Switcher Dropdown (Matching Helpdesk ViewBreadcrumbs) -->
            <Dropdown :options="viewDropdownOptions">
              <template #default="{ open }">
                <Button
                  variant="ghost"
                  class="font-semibold text-sm text-ink-gray-9 !bg-transparent hover:!bg-surface-gray-2 rounded-xl transition"
                >
                  <template #prefix>
                    <Icon :name="currentViewIcon" size="14" class="text-ink-gray-7" />
                  </template>
                  <span>{{ currentViewLabel }}</span>
                  <template #suffix>
                    <Icon
                      name="chevron-down"
                      size="13"
                      class="text-ink-gray-5 transition-transform"
                      :class="{ 'rotate-180': open }"
                    />
                  </template>
                </Button>
              </template>
            </Dropdown>
          </div>
        </template>

        <template #right-header>
          <!-- Dynamic Action Button: When multiple or all selected, switches from Create to Actions -->
          <Dropdown v-if="selectedTaskIds.length > 0" :options="bulkActionOptions" align="end">
            <template #default="{ open }">
              <Button
                theme="gray"
                variant="solid"
                size="sm"
                class="rounded-xl font-medium flex items-center gap-1.5 shadow-2xs"
              >
                <template #prefix>
                  <Icon name="check-square" size="13" />
                </template>
                <span>Actions ({{ selectedTaskIds.length }})</span>
                <template #suffix>
                  <Icon
                    name="chevron-down"
                    size="12"
                    class="transition-transform text-ink-gray-4"
                    :class="{ 'rotate-180': open }"
                  />
                </template>
              </Button>
            </template>
          </Dropdown>

          <!-- Standard '+ Create' button when nothing selected -->
          <Button
            v-else
            theme="gray"
            variant="solid"
            size="sm"
            class="rounded-xl font-medium"
            @click="$emit('open-new-task')"
          >
            <template #prefix>
              <Icon name="plus" size="14" />
            </template>
            <span>Create</span>
          </Button>
        </template>
      </LayoutHeader>

      <!-- Main Tasks Content -->
      <div class="flex-1 overflow-hidden relative">
        <div v-if="loading && tasks.length === 0" class="h-full flex items-center justify-center">
          <div class="flex items-center gap-2 text-xs text-ink-gray-5">
            <Icon name="refresh" size="16" class="animate-spin text-ink-gray-7" />
            <span>Loading tasks...</span>
          </div>
        </div>

        <!-- 1. List View (Replicated from Helpdesk Ticket List) -->
        <TaskListView
          v-else-if="activeView === 'list'"
          :tasks="tasks"
          :projects="projects"
          :modules="modules"
          :loading="loading"
          :selected-task-ids="selectedTaskIds"
          @update:selected-task-ids="selectedTaskIds = $event"
          @select-task="handleSelectTask"
          @update-status="handleQuickStatus"
          @reload="loadTasks"
          @filter-change="handleSubFilter"
        />

        <!-- 2. Kanban View -->
        <TaskKanbanView
          v-else-if="activeView === 'kanban'"
          :tasks="tasks"
          :modules="modules"
          @select-task="handleSelectTask"
          @update-status="handleQuickStatus"
          @filter-change="handleSubFilter"
        />

        <!-- 3. Calendar View -->
        <TaskCalendarView
          v-else-if="activeView === 'calendar'"
          :tasks="tasks"
          @select-task="handleSelectTask"
          @filter-change="handleSubFilter"
        />
      </div>
    </div>

    <!-- Bulk Edit Modal -->
    <BulkEditModal
      :show="showBulkEditModal"
      :task-ids="selectedTaskIds"
      :modules="modules"
      @close="showBulkEditModal = false"
      @updated="onBulkUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Dropdown, Button } from 'frappe-ui'
import Icon from '../components/Icon.vue'
import LayoutHeader from '../components/LayoutHeader.vue'
import TaskListView from '../components/TaskListView.vue'
import TaskKanbanView from '../components/TaskKanbanView.vue'
import TaskCalendarView from '../components/TaskCalendarView.vue'
import TaskTicketDetail from '../components/TaskTicketDetail.vue'
import BulkEditModal from '../components/BulkEditModal.vue'
import {
  getTasks,
  getTask,
  getProjects,
  getImplementationModules,
  quickUpdateStatus,
  bulkUpdateTasks,
  bulkDeleteTasks,
} from '../api'

defineEmits(['open-new-task'])

const route = useRoute()
const router = useRouter()

const activeView = ref(route.query.view || 'list')
const loading = ref(true)
const tasks = ref([])
const projects = ref([])
const modules = ref([])

// Bulk Selection & Modal State
const selectedTaskIds = ref([])
const showBulkEditModal = ref(false)

const currentTaskId = computed(() => {
  return route.params.taskId || route.query.select || null
})

const currentViewLabel = computed(() => {
  if (activeView.value === 'kanban') return 'Kanban'
  if (activeView.value === 'calendar') return 'Calendar'
  return 'List'
})

const currentViewIcon = computed(() => {
  if (activeView.value === 'kanban') return 'folder-kanban'
  if (activeView.value === 'calendar') return 'clock'
  return 'list'
})

const viewDropdownOptions = [
  {
    label: 'List View',
    icon: 'lucide-list',
    onClick: () => { activeView.value = 'list' },
  },
  {
    label: 'Kanban Board',
    icon: 'lucide-kanban',
    onClick: () => { activeView.value = 'kanban' },
  },
  {
    label: 'Calendar Schedule',
    icon: 'lucide-calendar',
    onClick: () => { activeView.value = 'calendar' },
  },
]

// Bulk Action Dropdown Options
const bulkActionOptions = computed(() => [
  {
    label: 'Bulk Edit Fields...',
    icon: 'lucide-edit-3',
    onClick: () => { showBulkEditModal.value = true },
  },
  {
    label: 'Mark as Completed',
    icon: 'lucide-check-circle',
    onClick: () => handleBulkStatus('Completed'),
  },
  {
    label: 'Mark as Working',
    icon: 'lucide-clock',
    onClick: () => handleBulkStatus('Working'),
  },
  {
    label: 'Mark as Open',
    icon: 'lucide-rotate-ccw',
    onClick: () => handleBulkStatus('Open'),
  },
  {
    label: 'Delete Selected Tasks',
    icon: 'lucide-trash-2',
    onClick: handleBulkDelete,
  },
  {
    label: 'Clear Selection',
    icon: 'lucide-x',
    onClick: () => { selectedTaskIds.value = [] },
  },
])

async function handleBulkStatus(status) {
  if (selectedTaskIds.value.length === 0) return
  try {
    await bulkUpdateTasks(selectedTaskIds.value, { status })
    selectedTaskIds.value = []
    await loadTasks()
  } catch (e) {
    alert('Failed to update tasks: ' + (e.message || e))
  }
}

async function handleBulkDelete() {
  if (selectedTaskIds.value.length === 0) return
  if (!confirm(`Are you sure you want to delete ${selectedTaskIds.value.length} selected tasks?`)) return
  try {
    await bulkDeleteTasks(selectedTaskIds.value)
    selectedTaskIds.value = []
    await loadTasks()
  } catch (e) {
    alert('Failed to delete tasks: ' + (e.message || e))
  }
}

async function onBulkUpdated() {
  selectedTaskIds.value = []
  await loadTasks()
}

const filters = ref({
  project: route.query.project || 'All',
  module: 'All',
  status: 'All',
  priority: 'All',
  assigned_to: route.query.assigned || 'All',
})

onMounted(async () => {
  await Promise.all([loadTasks(), loadMeta()])
})

watch(() => route.query.view, (newView) => {
  if (newView && newView !== activeView.value) {
    activeView.value = newView
    selectedTaskIds.value = []
  }
})

watch(activeView, (newView) => {
  if (!currentTaskId.value) {
    router.replace({ query: { ...route.query, view: newView } })
    selectedTaskIds.value = []
  }
})

watch(() => route.query.filter, (filterVal) => {
  if (filterVal === 'pending') {
    filters.value.status = 'Open'
  } else if (filterVal === 'overdue') {
    filters.value.is_overdue = 1
  } else if (filterVal === 'milestones') {
    filters.value.is_milestone = 1
  } else {
    delete filters.value.is_overdue
    delete filters.value.is_milestone
    filters.value.status = 'All'
  }
  loadTasks()
})

watch(() => route.query.assigned, (assignedVal) => {
  filters.value.assigned_to = assignedVal || 'All'
  loadTasks()
})

async function loadMeta() {
  try {
    const [pList, mList] = await Promise.all([
      getProjects(),
      getImplementationModules(),
    ])
    projects.value = pList || []
    modules.value = mList || []
  } catch (e) {
    console.error(e)
  }
}

async function loadTasks() {
  loading.value = true
  try {
    tasks.value = await getTasks(filters.value)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleSelectTask(taskId) {
  const task = tasks.value.find(item => item.name === taskId)
  if (task?.project) {
    router.push(`/projects/${task.project}/tasks/${taskId}`)
    return
  }
  router.push('/tasks/' + taskId)
}

watch(currentTaskId, async (taskId) => {
  if (!taskId) return
  const known = tasks.value.find(item => item.name === taskId)
  if (known?.project) {
    router.replace(`/projects/${known.project}/tasks/${taskId}`)
    return
  }
  if (known) return
  try {
    const data = await getTask(taskId)
    if (data?.project) router.replace(`/projects/${data.project}/tasks/${taskId}`)
  } catch (e) {
    console.error(e)
  }
}, { immediate: true })

function handleBackToList() {
  router.push({ path: '/tasks', query: { view: activeView.value } })
}

async function handleQuickStatus(taskId, status) {
  try {
    await quickUpdateStatus(taskId, status)
    const t = tasks.value.find(item => item.name === taskId)
    if (t) {
      t.status = status
      if (status === 'Completed') t.progress = 100
    }
  } catch (e) {
    alert('Failed to update status: ' + e.message)
  }
}

function handleSubFilter(subFilters) {
  filters.value = { ...filters.value, ...subFilters }
  loadTasks()
}
</script>
