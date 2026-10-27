<template>
  <div class="h-full flex flex-col overflow-hidden bg-surface-white">
    <!-- CASE 1: Individual Task Ticket Detail View (Helpdesk style) -->
    <template v-if="currentTaskId">
      <TaskTicketDetail
        :task-id="currentTaskId"
        :show-back="true"
        @back="handleBackToList"
        @updated="loadTasks"
      />
    </template>

    <!-- CASE 2: Tasks Explorer (List, Kanban, Calendar) -->
    <template v-else>
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
          <!-- Right Header matching Helpdesk: Solid Charcoal '+ Create' button only -->
          <Button
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
    </template>
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
import {
  getTasks,
  getProjects,
  getImplementationModules,
  quickUpdateStatus,
} from '../api'

defineEmits(['open-new-task'])

const route = useRoute()
const router = useRouter()

const activeView = ref(route.query.view || 'list')
const loading = ref(true)
const tasks = ref([])
const projects = ref([])
const modules = ref([])

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
  }
})

watch(activeView, (newView) => {
  if (!currentTaskId.value) {
    router.replace({ query: { ...route.query, view: newView } })
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
  router.push('/tasks/' + taskId)
}

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
