<template>
  <div class="h-full flex flex-col bg-surface-white overflow-hidden select-none">
    <!-- 1. Dedicated QuickFilters Sub-bar (Matching Frappe Helpdesk ListViewBuilder.vue 1:1) -->
    <div class="px-5 py-3 border-b border-outline-gray-1 bg-surface-white flex items-center justify-between gap-3 shrink-0">
      <!-- Left: Quick filter search fields (ID, Subject, Project, Module, Status, Priority) -->
      <div class="flex items-center gap-2 overflow-x-auto min-w-0 flex-1 py-0.5">
        <!-- ID Filter Input -->
        <div class="w-24">
          <TextInput
            v-model="searchId"
            placeholder="ID"
            size="sm"
          />
        </div>

        <!-- Subject Filter Input -->
        <div class="w-48 sm:w-56">
          <TextInput
            v-model="searchSubject"
            placeholder="Subject"
            size="sm"
          />
        </div>

        <!-- Project Link/Select -->
        <div class="w-44">
          <Select
            v-model="selectedProject"
            :options="projectOptions"
            size="sm"
          />
        </div>

        <!-- Module Select Filter -->
        <div class="w-44">
          <Select
            v-model="selectedModule"
            :options="moduleOptions"
            size="sm"
          />
        </div>

        <!-- Status Select -->
        <div class="w-36">
          <Select
            v-model="selectedStatus"
            :options="statusFilterOptions"
            size="sm"
          />
        </div>

        <!-- Priority Select -->
        <div class="w-32">
          <Select
            v-model="selectedPriority"
            :options="priorityFilterOptions"
            size="sm"
          />
        </div>

        <!-- Clear filters button if active -->
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1 rounded-lg hover:bg-surface-gray-2 transition flex items-center gap-1 shrink-0 cursor-pointer"
        >
          <span>✕</span>
          <span>Clear</span>
        </button>
      </div>

      <!-- Right: Action Controls matching Helpdesk (Reload, Filter, Sort, Columns) -->
      <div class="flex items-center gap-1.5 shrink-0">
        <!-- Reload Button -->
        <Button
          variant="ghost"
          size="sm"
          class="!p-1.5 !rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 text-ink-gray-6 hover:text-ink-gray-9 shadow-2xs cursor-pointer"
          title="Reload"
          :loading="loading"
          @click="$emit('reload')"
        >
          <template #prefix>
            <Icon name="refresh" size="14" />
          </template>
        </Button>

        <!-- Advance Filter Button with interactive toggle and active badge -->
        <Button
          variant="ghost"
          size="sm"
          class="!rounded-xl border border-outline-gray-2 text-xs shadow-2xs transition cursor-pointer"
          :class="showAdvancedFilter || activeAdvanceFilterCount > 0 ? '!bg-surface-gray-3 !border-outline-gray-4 text-ink-gray-9 font-semibold' : 'bg-surface-gray-1 hover:bg-surface-gray-2 text-ink-gray-7 hover:text-ink-gray-9'"
          :label="activeAdvanceFilterCount > 0 ? `Filter (${activeAdvanceFilterCount})` : 'Filter'"
          @click="showAdvancedFilter = !showAdvancedFilter"
        >
          <template #prefix>
            <Icon name="filter" size="13" />
          </template>
        </Button>

        <!-- Sort By Dropdown -->
        <Dropdown :options="sortOptions" align="end">
          <template #default="{ open }">
            <Button
              variant="ghost"
              size="sm"
              class="!rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 text-ink-gray-7 hover:text-ink-gray-9 text-xs flex items-center gap-1 shadow-2xs cursor-pointer"
            >
              <template #prefix>
                <Icon name="arrow-up-down" size="13" class="text-ink-gray-5" />
              </template>
              <span>{{ sortLabel }}</span>
              <template #suffix>
                <Icon name="chevron-down" size="12" class="text-ink-gray-4 transition-transform" :class="{ 'rotate-180': open }" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- Columns Dropdown -->
        <Dropdown :options="columnToggleOptions" align="end">
          <template #default>
            <Button
              variant="ghost"
              size="sm"
              class="!rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 text-ink-gray-7 hover:text-ink-gray-9 text-xs shadow-2xs cursor-pointer"
              label="Columns"
            >
              <template #prefix>
                <Icon name="columns" size="13" />
              </template>
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- 1b. Advance Filter Panel (Opens when clicking Filter) -->
    <div
      v-if="showAdvancedFilter"
      class="px-5 py-3 border-b border-outline-gray-2 bg-surface-gray-1/80 flex flex-wrap items-center justify-between gap-3 shrink-0 animate-in fade-in duration-150 text-xs"
    >
      <div class="flex flex-wrap items-center gap-3">
        <!-- Milestone Filter -->
        <div class="flex items-center gap-1.5">
          <span class="text-ink-gray-5 font-medium">Milestone:</span>
          <select
            v-model="advMilestone"
            class="px-2.5 py-1 text-xs rounded-xl border border-outline-gray-2 bg-white text-ink-gray-8 focus:outline-none cursor-pointer"
          >
            <option value="all">All Tasks</option>
            <option value="milestone_only">Key Milestones Only</option>
            <option value="non_milestone">Non-Milestones</option>
          </select>
        </div>

        <!-- Overdue Filter -->
        <div class="flex items-center gap-1.5">
          <span class="text-ink-gray-5 font-medium">Deadline:</span>
          <select
            v-model="advOverdue"
            class="px-2.5 py-1 text-xs rounded-xl border border-outline-gray-2 bg-white text-ink-gray-8 focus:outline-none cursor-pointer"
          >
            <option value="all">All Deadlines</option>
            <option value="overdue_only">Overdue Tasks Only</option>
            <option value="not_overdue">On Track / Not Overdue</option>
          </select>
        </div>

        <!-- Assignee Filter -->
        <div class="flex items-center gap-1.5">
          <span class="text-ink-gray-5 font-medium">Assignee:</span>
          <select
            v-model="advAssignee"
            class="px-2.5 py-1 text-xs rounded-xl border border-outline-gray-2 bg-white text-ink-gray-8 focus:outline-none cursor-pointer"
          >
            <option value="all">All Assignees</option>
            <option value="unassigned">Unassigned Only</option>
            <option value="assigned">Assigned Only</option>
          </select>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button
          v-if="activeAdvanceFilterCount > 0"
          type="button"
          @click="clearAdvanceFilters"
          class="text-xs text-ink-gray-5 hover:text-ink-gray-9 font-medium px-2 py-1 rounded-lg hover:bg-surface-gray-2 cursor-pointer transition"
        >
          Reset Filters
        </button>
        <button
          type="button"
          @click="showAdvancedFilter = false"
          class="text-xs text-ink-gray-4 hover:text-ink-gray-7 px-1.5 py-1 cursor-pointer"
          title="Close filter panel"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- 2. Clean, Spacious Table (Replicated directly from Helpdesk Ticket List) -->
    <div class="flex-1 overflow-auto">
      <table class="w-full text-left border-collapse">
        <!-- Table Header -->
        <thead class="bg-surface-gray-1 sticky top-0 z-10 border-b border-outline-gray-1 text-[11px] font-semibold text-ink-gray-5 uppercase tracking-wider select-none">
          <tr>
            <th class="py-3 px-4 w-10 text-center">
              <div class="flex items-center justify-center">
                <Checkbox
                  :model-value="isAllSelected"
                  @update:model-value="toggleSelectAll"
                />
              </div>
            </th>
            <th class="py-3 px-3 w-20">ID</th>
            <th class="py-3 px-3 min-w-[280px]">Subject</th>
            <th class="py-3 px-3 w-32">Status</th>
            <th class="py-3 px-3 w-28">Priority</th>
            <th class="py-3 px-3 w-40">Assigned To</th>
            <th class="py-3 px-3 w-48">Project</th>
            <!-- Ample width for Due Date so it never wraps onto multiple lines -->
            <th class="py-3 px-3 w-40 min-w-[140px] whitespace-nowrap">Due Date</th>
            <!-- Module column moved to the very last as requested -->
            <th class="py-3 px-4 w-44">Module</th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody class="divide-y divide-outline-gray-1 text-xs">
          <!-- Empty State -->
          <tr v-if="paginatedTasks.length === 0">
            <td colspan="9" class="py-20 text-center text-ink-gray-4 text-xs">
              <Icon name="ticket" size="28" class="mx-auto text-ink-gray-3 mb-2" />
              <div class="font-medium text-ink-gray-6">No tasks found</div>
              <div class="text-[11px] text-ink-gray-4 mt-0.5">Try adjusting your filter search criteria.</div>
            </td>
          </tr>

          <!-- Task Rows -->
          <tr
            v-for="task in paginatedTasks"
            :key="task.name"
            @click="$emit('select-task', task.name)"
            class="hover:bg-surface-gray-1/80 cursor-pointer transition select-none group h-12"
            :class="{ 'bg-surface-gray-1/40': effectiveSelectedIds.includes(task.name) }"
          >
            <!-- Checkbox (Using Frappe UI Checkbox) -->
            <td class="py-3 px-4 text-center" @click.stop>
              <div class="flex items-center justify-center">
                <Checkbox
                  :model-value="effectiveSelectedIds.includes(task.name)"
                  @update:model-value="() => toggleSelectTask(task.name)"
                />
              </div>
            </td>

            <!-- 1. ID Column (Bold like Helpdesk e.g. 0198) -->
            <td class="py-3 px-3 w-20 font-semibold text-ink-gray-9 text-xs">
              {{ cleanId(task.name) }}
            </td>

            <!-- 2. Subject Column (Bold like Helpdesk) -->
            <td class="py-3 px-3 min-w-[280px]">
              <div class="flex items-center gap-2 min-w-0">
                <Tooltip v-if="task.is_milestone" text="Key Milestone">
                  <span class="text-amber-500 shrink-0">
                    <Icon name="flag" size="13" />
                  </span>
                </Tooltip>
                <span class="font-semibold text-ink-gray-9 group-hover:text-ink-black transition truncate max-w-lg">
                  {{ task.subject }}
                </span>
              </div>
            </td>

            <!-- 3. Status Column (Clean Helpdesk Status with Color Dot: • Open) -->
            <td class="py-3 px-3 w-32" @click.stop>
              <Dropdown :options="getStatusOptions(task.name)" align="start">
                <template #default="{ open }">
                  <div class="inline-flex items-center gap-1.5 px-2 py-1 -ms-2 rounded-lg hover:bg-surface-gray-2 cursor-pointer transition text-xs text-ink-gray-8">
                    <span class="w-2 h-2 rounded-full shrink-0" :class="statusDotClass(task.status)"></span>
                    <span class="font-medium">{{ task.status || 'Open' }}</span>
                  </div>
                </template>
              </Dropdown>
            </td>

            <!-- 4. Priority Column (3-bar signal icon + clean label without duplication) -->
            <td class="py-3 px-3 w-28">
              <TicketPriority :priority="task.priority || 'Medium'" />
            </td>

            <!-- 5. Assigned To Column (Helpdesk Avatar + Full Name) -->
            <td class="py-3 px-3 w-40">
              <div v-if="task.assignees?.length > 0" class="flex items-center gap-2 min-w-0">
                <Avatar
                  size="sm"
                  :label="task.assignees[0].full_name || task.assignees[0].email"
                />
                <span class="text-xs text-ink-gray-8 truncate max-w-[110px]">
                  {{ task.assignees[0].full_name || task.assignees[0].email }}
                </span>
              </div>
              <span v-else class="text-xs text-ink-gray-4 italic">Unassigned</span>
            </td>

            <!-- 6. Project Column (Client Rollout Name) -->
            <td class="py-3 px-3 w-48 text-ink-gray-7 text-xs truncate max-w-[190px]">
              {{ task.project_title || task.project }}
            </td>

            <!-- 7. Due Date Column (AMPLE WIDTH: NEVER WRAPS) -->
            <td class="py-3 px-3 w-40 min-w-[140px] whitespace-nowrap">
              <div class="flex items-center gap-1.5 text-xs whitespace-nowrap" :class="task.is_overdue ? 'text-red-600 font-medium' : 'text-ink-gray-6'">
                <span>{{ formatDate(task.exp_end_date) }}</span>
                <Badge
                  v-if="task.is_overdue"
                  theme="red"
                  variant="subtle"
                  size="sm"
                  label="Overdue"
                />
              </div>
            </td>

            <!-- 8. Module Column (MOVED TO LAST WITH ROUND FULL CAPSULE PILL CORNERS) -->
            <td class="py-3 px-4 w-44">
              <span
                v-if="task.module_title"
                class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium border"
                :style="{
                  backgroundColor: (task.module_color || '#3B82F6') + '15',
                  borderColor: (task.module_color || '#3B82F6') + '30',
                  color: task.module_color || '#1E40AF',
                }"
              >
                <Icon :name="task.module_icon || 'package'" size="11" />
                <span class="truncate max-w-[120px]">{{ task.module_title }}</span>
              </span>
              <span v-else class="text-xs text-ink-gray-4">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 3. Table Footer (Matching Helpdesk Ticket List Pagination: 20 50 100 & Load More) -->
    <div class="px-5 py-3 border-t border-outline-gray-1 bg-surface-white flex items-center justify-between shrink-0 select-none text-xs">
      <!-- Left: Page length selector [ 20 ] [ 50 ] [ 100 ] -->
      <div class="flex items-center gap-1 p-0.5 rounded-xl bg-surface-gray-2 border border-outline-gray-2">
        <button
          v-for="size in [20, 50, 100]"
          :key="size"
          @click="pageSize = size"
          class="px-2.5 py-1 rounded-lg text-xs font-medium transition"
          :class="pageSize === size ? 'bg-white shadow-2xs text-ink-gray-9 font-semibold' : 'text-ink-gray-6 hover:text-ink-gray-9'"
        >
          {{ size }}
        </button>
      </div>

      <!-- Right: Load more button & count -->
      <div class="flex items-center gap-3">
        <Button
          v-if="hasMore"
          variant="subtle"
          size="sm"
          class="rounded-xl font-medium"
          label="Load More"
          @click="loadMore"
        />
        <span class="text-ink-gray-5 text-xs">
          {{ Math.min(pageSize, filteredTasks.length) }} of {{ filteredTasks.length }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Badge, Tooltip, Avatar, Dropdown, Button, Checkbox, TextInput, Select } from 'frappe-ui'
import Icon from './Icon.vue'
import TicketPriority from './TicketPriority.vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => [],
  },
  projects: {
    type: Array,
    default: () => [],
  },
  modules: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  selectedTaskIds: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits([
  'select-task',
  'update-status',
  'reload',
  'filter-change',
  'update:selectedTaskIds',
  'open-bulk-edit',
])

const SAVED_FILTERS_KEY = 'projects_task_list_saved_filters'

// Quick filter states
const searchId = ref('')
const searchSubject = ref('')
const selectedProject = ref('All')
const selectedModule = ref('All')
const selectedStatus = ref('All')
const selectedPriority = ref('All')
const sortKey = ref('exp_end_date')
const sortOrder = ref('asc')
const pageSize = ref(20)

const projectOptions = computed(() => [
  { label: 'All Projects', value: 'All' },
  ...props.projects.map(p => ({ label: p.project_name, value: p.name })),
])

const moduleOptions = computed(() => [
  { label: 'All Modules', value: 'All' },
  ...props.modules.map(m => ({ label: m.module_name, value: m.name || m.module_code })),
])

const statusFilterOptions = [
  { label: 'All Statuses', value: 'All' },
  { label: 'Open', value: 'Open' },
  { label: 'Working', value: 'Working' },
  { label: 'Pending Review', value: 'Pending Review' },
  { label: 'Completed', value: 'Completed' },
]

const priorityFilterOptions = [
  { label: 'All Priorities', value: 'All' },
  { label: 'Urgent', value: 'Urgent' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

// Advanced filter panel toggle & states
const showAdvancedFilter = ref(false)
const advMilestone = ref('all')
const advOverdue = ref('all')
const advAssignee = ref('all')

// Local multi-select fallback if not bound from parent
const localSelectedTaskIds = ref([])

const effectiveSelectedIds = computed(() => {
  return props.selectedTaskIds !== undefined && props.selectedTaskIds.length > 0
    ? props.selectedTaskIds
    : localSelectedTaskIds.value
})

onMounted(() => {
  loadSavedFilters()
})

function loadSavedFilters() {
  try {
    const raw = sessionStorage.getItem(SAVED_FILTERS_KEY)
    if (raw) {
      const saved = JSON.parse(raw)
      if (saved.searchId !== undefined) searchId.value = saved.searchId
      if (saved.searchSubject !== undefined) searchSubject.value = saved.searchSubject
      if (saved.selectedProject !== undefined) selectedProject.value = saved.selectedProject
      if (saved.selectedModule !== undefined) selectedModule.value = saved.selectedModule
      if (saved.selectedStatus !== undefined) selectedStatus.value = saved.selectedStatus
      if (saved.selectedPriority !== undefined) selectedPriority.value = saved.selectedPriority
      if (saved.advMilestone !== undefined) advMilestone.value = saved.advMilestone
      if (saved.advOverdue !== undefined) advOverdue.value = saved.advOverdue
      if (saved.advAssignee !== undefined) advAssignee.value = saved.advAssignee
      if (saved.showAdvancedFilter !== undefined) showAdvancedFilter.value = saved.showAdvancedFilter
      if (saved.sortKey !== undefined) sortKey.value = saved.sortKey
      if (saved.sortOrder !== undefined) sortOrder.value = saved.sortOrder
    }
  } catch (e) {
    console.warn('Failed to load saved task filters:', e)
  }
}

function persistFilters() {
  try {
    const filters = {
      searchId: searchId.value,
      searchSubject: searchSubject.value,
      selectedProject: selectedProject.value,
      selectedModule: selectedModule.value,
      selectedStatus: selectedStatus.value,
      selectedPriority: selectedPriority.value,
      advMilestone: advMilestone.value,
      advOverdue: advOverdue.value,
      advAssignee: advAssignee.value,
      showAdvancedFilter: showAdvancedFilter.value,
      sortKey: sortKey.value,
      sortOrder: sortOrder.value,
    }
    sessionStorage.setItem(SAVED_FILTERS_KEY, JSON.stringify(filters))
  } catch (e) {}
}

watch(
  [
    searchId,
    searchSubject,
    selectedProject,
    selectedModule,
    selectedStatus,
    selectedPriority,
    advMilestone,
    advOverdue,
    advAssignee,
    showAdvancedFilter,
    sortKey,
    sortOrder,
  ],
  () => {
    persistFilters()
  }
)

const activeAdvanceFilterCount = computed(() => {
  let count = 0
  if (advMilestone.value !== 'all') count++
  if (advOverdue.value !== 'all') count++
  if (advAssignee.value !== 'all') count++
  return count
})

const hasActiveFilters = computed(() => {
  return (
    searchId.value.trim() !== '' ||
    searchSubject.value.trim() !== '' ||
    selectedProject.value !== 'All' ||
    selectedModule.value !== 'All' ||
    selectedStatus.value !== 'All' ||
    selectedPriority.value !== 'All' ||
    activeAdvanceFilterCount.value > 0
  )
})

function clearAdvanceFilters() {
  advMilestone.value = 'all'
  advOverdue.value = 'all'
  advAssignee.value = 'all'
}

function clearFilters() {
  searchId.value = ''
  searchSubject.value = ''
  selectedProject.value = 'All'
  selectedModule.value = 'All'
  selectedStatus.value = 'All'
  selectedPriority.value = 'All'
  clearAdvanceFilters()
  try {
    sessionStorage.removeItem(SAVED_FILTERS_KEY)
  } catch (e) {}
}

// Client-side filtering & sorting
const filteredTasks = computed(() => {
  return props.tasks.filter((task) => {
    // 1. ID Filter
    if (searchId.value.trim()) {
      const q = searchId.value.trim().toLowerCase()
      const rawId = (task.name || '').toLowerCase()
      const shortId = cleanId(task.name).toLowerCase()
      if (!rawId.includes(q) && !shortId.includes(q)) return false
    }

    // 2. Subject Filter
    if (searchSubject.value.trim()) {
      const q = searchSubject.value.trim().toLowerCase()
      if (!(task.subject || '').toLowerCase().includes(q)) return false
    }

    // 3. Project Filter
    if (selectedProject.value !== 'All') {
      if (task.project !== selectedProject.value && task.project_name !== selectedProject.value) {
        return false
      }
    }

    // 4. Module Filter
    if (selectedModule.value !== 'All') {
      if (
        task.implementation_module !== selectedModule.value &&
        task.module_code !== selectedModule.value &&
        task.module_title !== selectedModule.value
      ) {
        return false
      }
    }

    // 5. Status Filter
    if (selectedStatus.value !== 'All') {
      if (task.status !== selectedStatus.value) return false
    }

    // 6. Priority Filter
    if (selectedPriority.value !== 'All') {
      if (task.priority !== selectedPriority.value) return false
    }

    // 7. Advance Filters
    if (advMilestone.value === 'milestone_only' && !task.is_milestone) return false
    if (advMilestone.value === 'non_milestone' && task.is_milestone) return false

    if (advOverdue.value === 'overdue_only' && !task.is_overdue) return false
    if (advOverdue.value === 'not_overdue' && task.is_overdue) return false

    if (advAssignee.value === 'unassigned' && (task.assignees?.length || 0) > 0) return false
    if (advAssignee.value === 'assigned' && (task.assignees?.length || 0) === 0) return false

    return true
  }).sort((a, b) => {
    let valA = a[sortKey.value] || ''
    let valB = b[sortKey.value] || ''
    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

const paginatedTasks = computed(() => {
  return filteredTasks.value.slice(0, pageSize.value)
})

const hasMore = computed(() => {
  return filteredTasks.value.length > pageSize.value
})

function loadMore() {
  pageSize.value += 20
}

const isAllSelected = computed(() => {
  if (paginatedTasks.value.length === 0) return false
  return paginatedTasks.value.every((t) => effectiveSelectedIds.value.includes(t.name))
})

function toggleSelectAll() {
  let updated = []
  if (!isAllSelected.value) {
    updated = paginatedTasks.value.map((t) => t.name)
  }
  localSelectedTaskIds.value = updated
  emit('update:selectedTaskIds', updated)
}

function toggleSelectTask(id) {
  const current = [...effectiveSelectedIds.value]
  const idx = current.indexOf(id)
  if (idx > -1) {
    current.splice(idx, 1)
  } else {
    current.push(id)
  }
  localSelectedTaskIds.value = current
  emit('update:selectedTaskIds', current)
}

function cleanId(rawName) {
  if (!rawName) return '0000'
  const parts = rawName.split('-')
  return parts.length > 1 ? parts[parts.length - 1] : rawName
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr.split(' ')[0])
    if (isNaN(d.getTime())) return dateStr
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch (e) {
    return dateStr
  }
}

function statusDotClass(status) {
  if (status === 'Completed') return 'bg-emerald-500'
  if (status === 'Working') return 'bg-blue-600'
  if (status === 'Pending Review') return 'bg-amber-500'
  if (status === 'Cancelled') return 'bg-ink-gray-4'
  return 'bg-red-500' // Open
}

function getStatusOptions(taskId) {
  return [
    { label: 'Open', onClick: () => emit('update-status', taskId, 'Open') },
    { label: 'Working', onClick: () => emit('update-status', taskId, 'Working') },
    { label: 'Pending Review', onClick: () => emit('update-status', taskId, 'Pending Review') },
    { label: 'Completed', onClick: () => emit('update-status', taskId, 'Completed') },
    { label: 'Cancelled', onClick: () => emit('update-status', taskId, 'Cancelled') },
  ]
}

const sortLabel = computed(() => {
  if (sortKey.value === 'exp_end_date') return 'Due Date'
  if (sortKey.value === 'subject') return 'Subject'
  if (sortKey.value === 'priority') return 'Priority'
  if (sortKey.value === 'status') return 'Status'
  return 'Sort By'
})

const sortOptions = [
  { label: 'Due Date', onClick: () => { sortKey.value = 'exp_end_date' } },
  { label: 'Subject', onClick: () => { sortKey.value = 'subject' } },
  { label: 'Priority', onClick: () => { sortKey.value = 'priority' } },
  { label: 'Status', onClick: () => { sortKey.value = 'status' } },
]

const columnToggleOptions = [
  { label: 'ID', disabled: true },
  { label: 'Subject', disabled: true },
  { label: 'Status' },
  { label: 'Priority' },
  { label: 'Assigned To' },
  { label: 'Project' },
  { label: 'Due Date' },
  { label: 'Module' },
]

</script>
