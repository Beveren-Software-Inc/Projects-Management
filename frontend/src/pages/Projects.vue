<template>
  <div class="h-full flex flex-col bg-[#f8f9fa] overflow-hidden select-none">
    <!-- 1. Layout Header matching Helpdesk -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-2.5">
          <h1 class="text-sm font-semibold text-ink-gray-9">Projects</h1>
          <Badge theme="gray" variant="subtle" size="sm" :label="projects.length + ' Projects'" />

          <!-- Quick Stage / Status Filter Chips -->
          <div class="hidden md:flex items-center gap-1.5 ml-2 pl-3 border-l border-outline-gray-2 text-xs">
            <button
              type="button"
              @click="quickFilter = 'all'"
              class="px-2.5 py-0.5 rounded-full text-xs transition cursor-pointer font-medium"
              :class="quickFilter === 'all' ? 'bg-ink-gray-9 text-white shadow-2xs' : 'bg-surface-gray-2 text-ink-gray-6 hover:bg-surface-gray-3 hover:text-ink-gray-9'"
            >
              All ({{ projects.length }})
            </button>
            <button
              type="button"
              @click="quickFilter = 'active'"
              class="px-2.5 py-0.5 rounded-full text-xs transition cursor-pointer font-medium flex items-center gap-1"
              :class="quickFilter === 'active' ? 'bg-surface-blue-7 text-white shadow-2xs' : 'bg-surface-blue-2 text-ink-blue-7 hover:bg-surface-blue-3 border border-outline-blue-2'"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-blue-500" :class="{ 'bg-white': quickFilter === 'active' }"></span>
              Active ({{ activeCount }})
            </button>
            <button
              type="button"
              @click="quickFilter = 'uat'"
              class="px-2.5 py-0.5 rounded-full text-xs transition cursor-pointer font-medium flex items-center gap-1"
              :class="quickFilter === 'uat' ? 'bg-surface-amber-7 text-white shadow-2xs' : 'bg-surface-amber-2 text-ink-amber-7 hover:bg-surface-amber-3 border border-outline-amber-2'"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-amber-500" :class="{ 'bg-white': quickFilter === 'uat' }"></span>
              UAT / Go-Live ({{ uatCount }})
            </button>
            <button
              type="button"
              @click="quickFilter = 'completed'"
              class="px-2.5 py-0.5 rounded-full text-xs transition cursor-pointer font-medium flex items-center gap-1"
              :class="quickFilter === 'completed' ? 'bg-surface-green-7 text-white shadow-2xs' : 'bg-surface-green-2 text-ink-green-7 hover:bg-surface-green-3 border border-outline-green-2'"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-green-500" :class="{ 'bg-white': quickFilter === 'completed' }"></span>
              Completed ({{ completedCount }})
            </button>
          </div>
        </div>
      </template>

      <template #right-header>
        <div class="flex items-center gap-2">
          <!-- Refresh -->
          <Button
            variant="ghost"
            size="sm"
            class="!p-1.5 !rounded-xl border border-outline-gray-2 bg-white hover:bg-surface-gray-2 text-ink-gray-7 shadow-2xs cursor-pointer"
            title="Refresh"
            @click="loadProjects"
          >
            <template #prefix>
              <Icon name="refresh" size="13" :class="{ 'animate-spin': loading }" />
            </template>
          </Button>

          <!-- + New Project Button -->
          <Button
            theme="gray"
            variant="solid"
            size="sm"
            label="New Project"
            @click="$emit('open-new-project')"
          >
            <template #prefix>
              <Icon name="plus" size="13" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <!-- 2. Interactive Filter & Search Sub-bar -->
    <div class="px-6 py-3 bg-white border-b border-outline-gray-2 flex items-center justify-between gap-3 shrink-0">
      <div class="flex items-center gap-2.5 flex-1 min-w-0">
        <!-- Search Input -->
        <div class="w-72">
          <TextInput
            v-model="searchQuery"
            placeholder="Search projects, client, PoC..."
            size="sm"
          >
            <template #prefix>
              <Icon name="search" size="13" class="text-ink-gray-4" />
            </template>
          </TextInput>
        </div>

        <!-- Stage Filter Select -->
        <div class="w-48">
          <Select
            v-model="stageFilter"
            :options="[
              { label: 'All Stages', value: 'All' },
              { label: 'Discovery', value: 'Discovery' },
              { label: 'Design', value: 'Design' },
              { label: 'Configuration & Customization', value: 'Configuration & Customization' },
              { label: 'Data Migration', value: 'Data Migration' },
              { label: 'UAT & Training', value: 'UAT & Training' },
              { label: 'Go-Live', value: 'Go-Live' },
              { label: 'Hypercare Support', value: 'Hypercare Support' },
              { label: 'Closed', value: 'Closed' },
            ]"
            size="sm"
          />
        </div>

        <!-- Status Filter Select -->
        <div class="w-36">
          <Select
            v-model="statusFilter"
            :options="[
              { label: 'All Statuses', value: 'All' },
              { label: 'Open', value: 'Open' },
              { label: 'Completed', value: 'Completed' },
              { label: 'Cancelled', value: 'Cancelled' },
            ]"
            size="sm"
          />
        </div>

        <!-- Clear filters button if active -->
        <Button
          v-if="searchQuery || stageFilter !== 'All' || statusFilter !== 'All' || quickFilter !== 'all'"
          variant="ghost"
          size="sm"
          label="Reset Filters"
          @click="clearFilters"
        />
      </div>

      <!-- Right: Showing Count -->
      <div class="text-xs text-ink-gray-5 shrink-0 hidden sm:block">
        Showing <span class="font-semibold text-ink-gray-9">{{ filteredProjects.length }}</span> of {{ projects.length }} projects
      </div>
    </div>

    <!-- 3. Main Content Area: Scrollable Card Grid -->
    <div class="flex-1 overflow-y-auto p-6">
      <!-- Loading State -->
      <div v-if="loading" class="py-20 text-center text-xs text-ink-gray-4">
        <Icon name="refresh" size="20" class="animate-spin text-ink-gray-7 mb-2 mx-auto" />
        <div class="font-medium text-ink-gray-7">Loading implementation rollouts...</div>
        <div class="text-[11px] text-ink-gray-4 mt-0.5">Fetching module progress and task completion rates.</div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredProjects.length === 0"
        class="py-24 text-center max-w-md mx-auto space-y-3"
      >
        <div class="w-14 h-14 rounded-2xl bg-white border border-outline-gray-2 shadow-2xs flex items-center justify-center mx-auto text-ink-gray-4">
          <Icon name="folder-kanban" size="26" />
        </div>
        <div>
          <h3 class="text-sm font-semibold text-ink-gray-9">No Projects Found</h3>
          <p class="text-xs text-ink-gray-5 mt-1">
            {{ searchQuery || stageFilter !== 'All' || statusFilter !== 'All'
              ? 'No implementation rollouts match the selected filter criteria. Try resetting your search filters.'
              : 'You have not added any client implementation projects yet. Click "New Project" to create your first rollout.' }}
          </p>
        </div>
        <div class="pt-2">
          <Button
            v-if="searchQuery || stageFilter !== 'All' || statusFilter !== 'All'"
            variant="subtle"
            size="sm"
            label="Reset Filters"
            @click="clearFilters"
          />
          <Button
            v-else
            theme="gray"
            variant="solid"
            size="sm"
            label="Create New Project"
            @click="$emit('open-new-project')"
          />
        </div>
      </div>

      <!-- Project Cards Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="p in filteredProjects"
          :key="p.name"
          @click="$router.push('/projects/' + p.name)"
          class="bg-white rounded-2xl border border-outline-gray-2 shadow-2xs hover:shadow-md hover:border-outline-blue-3 transition-all duration-200 p-5 flex flex-col justify-between group relative overflow-hidden cursor-pointer select-none space-y-4"
        >
          <!-- Top Accent Color Bar tailored to Implementation Stage -->
          <div
            class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r"
            :class="getStageGradient(p.implementation_stage)"
          ></div>

          <!-- Section 1: Card Header -->
          <div>
            <div class="flex items-start justify-between gap-3 mb-3">
              <!-- Stage & Status Badges -->
              <div class="flex items-center gap-1.5 flex-wrap">
                <Badge
                  :theme="getStageTheme(p.implementation_stage)"
                  variant="subtle"
                  size="sm"
                  :label="p.implementation_stage || 'Discovery'"
                />
                <Badge
                  v-if="p.status === 'Completed'"
                  theme="green"
                  variant="subtle"
                  size="sm"
                  label="Completed"
                />
                <Badge
                  v-else-if="p.status === 'Cancelled'"
                  theme="red"
                  variant="subtle"
                  size="sm"
                  label="Cancelled"
                />
                <Badge
                  v-else
                  theme="gray"
                  variant="subtle"
                  size="sm"
                  label="Open"
                />
              </div>

              <!-- Project ID Monospace Badge -->
              <span class="text-[10px] font-mono text-ink-gray-5 bg-surface-gray-2 px-2 py-0.5 rounded-md border border-outline-gray-2 shrink-0">
                #{{ cleanId(p.name) }}
              </span>
            </div>

            <!-- Project Title -->
            <h2 class="text-sm font-semibold text-ink-gray-9 group-hover:text-ink-blue-7 transition line-clamp-1">
              {{ p.project_name }}
            </h2>
            <div class="text-[11px] text-ink-gray-4 mt-0.5 flex items-center gap-1">
              <span>{{ p.project_type || 'Implementation Rollout' }}</span>
              <span v-if="p.customer">• {{ p.customer }}</span>
            </div>
          </div>

          <!-- Section 2: Stakeholders -->
          <div class="p-3 bg-surface-gray-1 rounded-xl border border-outline-gray-2/70 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-[11px] text-ink-gray-5 font-medium">Client Contact:</span>
              <div class="flex items-center gap-1.5 min-w-0">
                <Avatar :label="p.client_poc_name || 'Client'" size="xs" />
                <span class="font-medium text-ink-gray-8 truncate max-w-[140px]">
                  {{ p.client_poc_name || 'Not assigned' }}
                </span>
              </div>
            </div>

            <div class="flex items-center justify-between pt-1 border-t border-outline-gray-2/50 text-[11px]">
              <span class="text-ink-gray-5">Project Lead:</span>
              <span class="font-medium text-ink-gray-7 truncate max-w-[140px]">
                {{ p.project_manager || p.owner || 'Lead PM' }}
              </span>
            </div>
          </div>

          <!-- Section 3: Scope Modules -->
          <div class="space-y-1.5">
            <div class="flex items-center justify-between text-[11px] text-ink-gray-5">
              <span>Scope Modules ({{ (p.modules || []).length }})</span>
              <span>{{ p.completed_tasks || 0 }}/{{ p.total_tasks || 0 }} tasks</span>
            </div>
            <div class="flex flex-wrap gap-1 max-h-12 overflow-hidden">
              <Badge
                v-for="m in (p.modules || []).slice(0, 4)"
                :key="m.module"
                theme="gray"
                variant="subtle"
                size="sm"
                :label="m.module_name"
              />
              <span v-if="(p.modules || []).length > 4" class="text-[10px] text-ink-gray-4 self-center font-mono">
                +{{ (p.modules || []).length - 4 }} more
              </span>
            </div>
          </div>

          <!-- Section 4: Progress Bar & Timeline Footer -->
          <div class="pt-3.5 border-t border-outline-gray-2 space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-[11px] text-ink-gray-5 font-medium">Rollout Completion</span>
              <span class="font-bold text-xs text-ink-gray-9">
                {{ p.percent_complete || 0 }}%
              </span>
            </div>

            <Progress :value="p.percent_complete || 0" size="sm" />

            <!-- Dates & View Project Action -->
            <div class="flex items-center justify-between text-[11px] text-ink-gray-5 pt-1">
              <div class="flex items-center gap-1.5 text-ink-gray-5">
                <Icon name="calendar" size="12" class="text-ink-gray-4" />
                <span>{{ formatDate(p.expected_start_date) }}</span>
                <span class="text-ink-gray-3">→</span>
                <span>{{ formatDate(p.expected_end_date) }}</span>
              </div>

              <div class="text-ink-blue-7 font-medium group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
                <span>View</span>
                <Icon name="chevron-right" size="12" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Badge,
  Button,
  Avatar,
  Progress,
  TextInput,
  Select,
} from 'frappe-ui'
import Icon from '../components/Icon.vue'
import LayoutHeader from '../components/LayoutHeader.vue'
import { getProjects } from '../api'

defineEmits(['open-new-project'])

const projects = ref([])
const loading = ref(true)
const searchQuery = ref('')
const stageFilter = ref('All')
const statusFilter = ref('All')
const quickFilter = ref('all')

onMounted(async () => {
  await loadProjects()
})

async function loadProjects() {
  loading.value = true
  try {
    projects.value = await getProjects({ status: 'All' })
  } catch (e) {
    console.error('Failed to load projects:', e)
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  searchQuery.value = ''
  stageFilter.value = 'All'
  statusFilter.value = 'All'
  quickFilter.value = 'all'
}

const filteredProjects = computed(() => {
  return projects.value.filter(p => {
    if (quickFilter.value === 'active' && p.status !== 'Open') return false
    if (quickFilter.value === 'completed' && p.status !== 'Completed') return false
    if (quickFilter.value === 'uat') {
      const stage = (p.implementation_stage || '').toLowerCase()
      if (!stage.includes('uat') && !stage.includes('go-live')) return false
    }

    if (statusFilter.value !== 'All' && p.status !== statusFilter.value) {
      return false
    }

    if (stageFilter.value !== 'All' && p.implementation_stage !== stageFilter.value) {
      return false
    }

    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      const nameMatch = (p.project_name || '').toLowerCase().includes(q)
      const idMatch = (p.name || '').toLowerCase().includes(q)
      const clientMatch = (p.client_poc_name || '').toLowerCase().includes(q)
      const emailMatch = (p.client_poc_email || '').toLowerCase().includes(q)
      const customerMatch = (p.customer || '').toLowerCase().includes(q)
      const moduleMatch = (p.modules || []).some(m => (m.module_name || '').toLowerCase().includes(q))
      if (!nameMatch && !idMatch && !clientMatch && !emailMatch && !customerMatch && !moduleMatch) {
        return false
      }
    }

    return true
  })
})

const activeCount = computed(() => {
  return projects.value.filter(p => p.status === 'Open').length
})

const completedCount = computed(() => {
  return projects.value.filter(p => p.status === 'Completed').length
})

const uatCount = computed(() => {
  return projects.value.filter(p => {
    const s = (p.implementation_stage || '').toLowerCase()
    return s.includes('uat') || s.includes('go-live')
  }).length
})

function cleanId(id) {
  if (!id) return ''
  return id.replace(/^PROJ-/, '')
}

function getStageGradient(stage) {
  const key = String(stage || '').toLowerCase()
  if (key.includes('discovery')) return 'from-purple-500 to-indigo-500'
  if (key.includes('design')) return 'from-indigo-500 to-blue-500'
  if (key.includes('configuration')) return 'from-blue-500 to-cyan-500'
  if (key.includes('data migration')) return 'from-amber-500 to-orange-500'
  if (key.includes('uat')) return 'from-orange-500 to-amber-600'
  if (key.includes('go-live')) return 'from-emerald-500 to-teal-500'
  if (key.includes('hypercare')) return 'from-teal-500 to-emerald-500'
  return 'from-slate-400 to-slate-500'
}

function getStageTheme(stage) {
  const key = String(stage || '').toLowerCase()
  if (key.includes('discovery') || key.includes('design')) return 'purple'
  if (key.includes('configuration')) return 'blue'
  if (key.includes('data') || key.includes('uat')) return 'amber'
  if (key.includes('go-live') || key.includes('hypercare')) return 'green'
  return 'gray'
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
</script>
