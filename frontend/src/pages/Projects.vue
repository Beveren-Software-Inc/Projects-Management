<template>
  <div class="h-full flex flex-col app-canvas overflow-hidden select-none">
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
              :class="quickFilter === 'active' ? 'bg-blue-600 text-white shadow-2xs' : 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200/60'"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-blue-500" :class="{ 'bg-white': quickFilter === 'active' }"></span>
              Active ({{ activeCount }})
            </button>
            <button
              type="button"
              @click="quickFilter = 'uat'"
              class="px-2.5 py-0.5 rounded-full text-xs transition cursor-pointer font-medium flex items-center gap-1"
              :class="quickFilter === 'uat' ? 'bg-amber-600 text-white shadow-2xs' : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200/60'"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-amber-500" :class="{ 'bg-white': quickFilter === 'uat' }"></span>
              UAT / Go-Live ({{ uatCount }})
            </button>
            <button
              type="button"
              @click="quickFilter = 'completed'"
              class="px-2.5 py-0.5 rounded-full text-xs transition cursor-pointer font-medium flex items-center gap-1"
              :class="quickFilter === 'completed' ? 'bg-emerald-600 text-white shadow-2xs' : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200/60'"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" :class="{ 'bg-white': quickFilter === 'completed' }"></span>
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

          <!-- Frappe UI Charcoal Button: + New Project -->
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
      <!-- Left: Search and Dropdowns -->
      <div class="flex items-center gap-2.5 flex-1 min-w-0">
        <!-- Search Input -->
        <div class="relative w-72">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search projects, client, PoC..."
            class="w-full pl-8 pr-3 py-1.5 text-xs bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white rounded-xl border border-outline-gray-2 focus:border-outline-gray-4 focus:outline-none placeholder:text-ink-gray-4 text-ink-gray-9 transition shadow-2xs"
          />
          <Icon name="search" size="13" class="absolute left-2.5 top-2.5 text-ink-gray-4" />
          <button
            v-if="searchQuery"
            type="button"
            @click="searchQuery = ''"
            class="absolute right-2.5 top-2 text-ink-gray-4 hover:text-ink-gray-7 text-xs"
          >
            ✕
          </button>
        </div>

        <!-- Stage Filter Select -->
        <select
          v-model="stageFilter"
          class="px-3 py-1.5 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white text-ink-gray-8 focus:outline-none transition shadow-2xs cursor-pointer"
        >
          <option value="All">All Stages</option>
          <option value="Discovery">Discovery</option>
          <option value="Design">Design</option>
          <option value="Configuration & Customization">Configuration & Customization</option>
          <option value="Data Migration">Data Migration</option>
          <option value="UAT & Training">UAT & Training</option>
          <option value="Go-Live">Go-Live</option>
          <option value="Hypercare Support">Hypercare Support</option>
          <option value="Closed">Closed</option>
        </select>

        <!-- Status Filter Select -->
        <select
          v-model="statusFilter"
          class="px-3 py-1.5 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white text-ink-gray-8 focus:outline-none transition shadow-2xs cursor-pointer"
        >
          <option value="All">All Statuses</option>
          <option value="Open">Open</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>

        <!-- Clear filters button if active -->
        <button
          v-if="searchQuery || stageFilter !== 'All' || statusFilter !== 'All' || quickFilter !== 'all'"
          @click="clearFilters"
          class="text-xs text-ink-gray-5 hover:text-ink-gray-9 px-2 py-1 rounded-lg hover:bg-surface-gray-2 transition flex items-center gap-1 shrink-0 cursor-pointer"
        >
          <span>✕</span>
          <span>Reset Filters</span>
        </button>
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

      <!-- Vibrant, Modern Project Cards Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="p in filteredProjects"
          :key="p.name"
          @click="$router.push('/projects/' + p.name)"
          class="bg-white rounded-2xl border border-outline-gray-2 shadow-2xs hover:shadow-md hover:border-blue-300 transition-all duration-200 p-5 flex flex-col justify-between group relative overflow-hidden cursor-pointer select-none space-y-4"
        >
          <!-- Top Accent Color Bar tailored to Implementation Stage -->
          <div
            class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r"
            :class="getStageGradient(p.implementation_stage)"
          ></div>

          <!-- Section 1: Card Header (Icon Box + Project Title + Stage & Status Badges) -->
          <div>
            <div class="flex items-start justify-between gap-3 mb-3">
              <!-- Stage & Status Badges -->
              <div class="flex items-center gap-1.5 flex-wrap">
                <!-- Implementation Stage Badge -->
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border shadow-2xs select-none"
                  :class="getStageBadgeClasses(p.implementation_stage)"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full shrink-0"
                    :style="{ backgroundColor: getStageColor(p.implementation_stage) }"
                  ></span>
                  <span>{{ p.implementation_stage || 'Discovery' }}</span>
                </span>

                <!-- Status Badge -->
                <span
                  v-if="p.status === 'Completed'"
                  class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs"
                >
                  <Icon name="check" size="11" />
                  <span>Completed</span>
                </span>
                <span
                  v-else-if="p.status === 'Cancelled'"
                  class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-red-50 text-red-700 border border-red-200 shadow-2xs"
                >
                  <span>Cancelled</span>
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-surface-gray-2 text-ink-gray-7 border border-outline-gray-2 shadow-2xs"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span>Open</span>
                </span>
              </div>

              <!-- Project ID Monospace Badge -->
              <span class="text-[10px] font-mono text-ink-gray-5 bg-surface-gray-2 px-2 py-0.5 rounded-md border border-outline-gray-2 shrink-0">
                #{{ cleanId(p.name) }}
              </span>
            </div>

            <!-- Project Identity: Squircle Icon + Name -->
            <div class="flex items-start gap-3">
              <!-- Vibrant Squircle Icon Box -->
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border shadow-2xs transition-transform duration-200 group-hover:scale-105"
                :style="{
                  backgroundColor: getStageColor(p.implementation_stage) + '18',
                  borderColor: getStageColor(p.implementation_stage) + '35',
                  color: getStageColor(p.implementation_stage)
                }"
              >
                <Icon
                  :name="getStageIcon(p.implementation_stage)"
                  size="18"
                  :color="getStageColor(p.implementation_stage)"
                />
              </div>

              <div class="min-w-0 flex-1">
                <h3 class="font-semibold text-sm text-ink-gray-9 group-hover:text-blue-600 transition line-clamp-1 leading-snug">
                  {{ p.project_name }}
                </h3>
                <div class="text-[11px] text-ink-gray-5 truncate mt-0.5 flex items-center gap-1.5">
                  <span v-if="p.customer" class="font-medium text-ink-gray-7">{{ p.customer }}</span>
                  <span v-if="p.customer" class="text-ink-gray-3">•</span>
                  <span>{{ p.project_type || 'Implementation' }}</span>
                </div>
              </div>
            </div>

            <!-- Section 2: Client PoC Details -->
            <div class="mt-3.5 pt-3 border-t border-outline-gray-2 flex items-center justify-between text-xs">
              <div class="flex items-center gap-2.5 min-w-0">
                <!-- Colorful Avatar Circle -->
                <div
                  class="w-7 h-7 rounded-full flex items-center justify-center font-semibold text-[11px] shrink-0 shadow-2xs border text-white"
                  :class="getClientAvatarGradient(p.client_poc_name || p.project_name)"
                >
                  {{ (p.client_poc_name || p.project_name || 'C').charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0 truncate">
                  <div class="font-medium text-ink-gray-8 truncate text-xs">
                    {{ p.client_poc_name || 'Client Representative' }}
                  </div>
                  <div v-if="p.client_poc_email" class="text-[11px] text-ink-gray-5 truncate flex items-center gap-1">
                    <Icon name="mail" size="10" class="text-ink-gray-4 shrink-0" />
                    <span class="truncate">{{ p.client_poc_email }}</span>
                  </div>
                </div>
              </div>

              <!-- Quick Task Count Chip -->
              <div class="text-[11px] text-ink-gray-5 shrink-0 bg-surface-gray-1 px-2 py-1 rounded-lg border border-outline-gray-2">
                <span class="font-semibold text-ink-gray-8">{{ p.completed_tasks || 0 }}</span>/{{ p.total_tasks || 0 }} tasks
              </div>
            </div>

            <!-- Section 3: Modules in Scope (Vibrant Colored Badges with Icons) -->
            <div class="mt-3 space-y-1.5">
              <div class="text-[10px] uppercase font-semibold text-ink-gray-4 tracking-wider flex items-center justify-between">
                <span>Modules in Scope</span>
                <span class="text-ink-gray-5 font-medium">({{ p.modules?.length || 0 }})</span>
              </div>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="m in (p.modules || []).slice(0, 5)"
                  :key="m.module || m.module_name"
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-lg text-[10px] font-medium border shadow-2xs select-none transition group-hover:shadow-xs"
                  :style="{
                    backgroundColor: (m.color || getModuleColor(m.module_name)) + '14',
                    borderColor: (m.color || getModuleColor(m.module_name)) + '32',
                    color: m.color || getModuleColor(m.module_name),
                  }"
                >
                  <Icon
                    :name="m.icon || getModuleIcon(m.module_name)"
                    size="11"
                    :color="m.color || getModuleColor(m.module_name)"
                  />
                  <span class="truncate max-w-[130px]">{{ m.module_name }}</span>
                </span>
                <span
                  v-if="(p.modules || []).length > 5"
                  class="inline-flex items-center px-1.5 py-0.5 rounded-md text-[10px] font-medium bg-surface-gray-2 text-ink-gray-6 border border-outline-gray-2"
                >
                  +{{ (p.modules || []).length - 5 }} more
                </span>
                <span
                  v-if="!p.modules || p.modules.length === 0"
                  class="text-[11px] text-ink-gray-4 italic"
                >
                  No modules attached
                </span>
              </div>
            </div>
          </div>

          <!-- Section 4: Progress Bar & Timeline Footer -->
          <div class="pt-3.5 border-t border-outline-gray-2 space-y-2">
            <!-- Progress numbers -->
            <div class="flex items-center justify-between text-xs">
              <span class="text-[11px] text-ink-gray-5 font-medium">Rollout Completion</span>
              <span
                class="font-bold text-xs"
                :class="p.percent_complete === 100 ? 'text-emerald-600' : 'text-blue-600'"
              >
                {{ p.percent_complete || 0 }}%
              </span>
            </div>

            <!-- Colorful Progress Bar -->
            <div class="w-full h-2 bg-surface-gray-2 rounded-full overflow-hidden p-0.5 border border-outline-gray-2/70">
              <div
                class="h-full rounded-full transition-all duration-500 shadow-2xs"
                :class="p.percent_complete === 100 ? 'bg-emerald-500' : 'bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600'"
                :style="{ width: Math.max(p.percent_complete || 0, 2) + '%' }"
              ></div>
            </div>

            <!-- Dates & View Project Action -->
            <div class="flex items-center justify-between text-[11px] text-ink-gray-5 pt-1">
              <div class="flex items-center gap-1.5 text-ink-gray-5">
                <Icon name="calendar" size="12" class="text-ink-gray-4" />
                <span>{{ formatDate(p.expected_start_date) }}</span>
                <span class="text-ink-gray-3">→</span>
                <span>{{ formatDate(p.expected_end_date) }}</span>
              </div>

              <div class="text-blue-600 font-medium group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
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
import { Badge, Button } from 'frappe-ui'
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

// Filtered projects computed
const filteredProjects = computed(() => {
  return projects.value.filter(p => {
    // Quick filter chips
    if (quickFilter.value === 'active' && p.status !== 'Open') return false
    if (quickFilter.value === 'completed' && p.status !== 'Completed') return false
    if (quickFilter.value === 'uat') {
      const stage = (p.implementation_stage || '').toLowerCase()
      if (!stage.includes('uat') && !stage.includes('go-live')) return false
    }

    // Status filter
    if (statusFilter.value !== 'All' && p.status !== statusFilter.value) {
      return false
    }

    // Stage filter
    if (stageFilter.value !== 'All' && p.implementation_stage !== stageFilter.value) {
      return false
    }

    // Search query (matches project_name, name, customer, PoC, or module names)
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

// Stage Meta & Styling
const STAGE_CONFIG = {
  'discovery': { color: '#8B5CF6', icon: 'search', gradient: 'from-purple-500 to-indigo-500', badge: 'bg-purple-50 text-purple-700 border-purple-200' },
  'design': { color: '#6366F1', icon: 'layout', gradient: 'from-indigo-500 to-blue-500', badge: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  'configuration': { color: '#3B82F6', icon: 'settings', gradient: 'from-blue-500 to-cyan-500', badge: 'bg-blue-50 text-blue-700 border-blue-200' },
  'data migration': { color: '#F59E0B', icon: 'database', gradient: 'from-amber-500 to-orange-500', badge: 'bg-amber-50 text-amber-700 border-amber-200' },
  'uat': { color: '#F97316', icon: 'users', gradient: 'from-orange-500 to-amber-600', badge: 'bg-orange-50 text-orange-700 border-orange-200' },
  'go-live': { color: '#10B981', icon: 'award', gradient: 'from-emerald-500 to-teal-500', badge: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  'hypercare': { color: '#14B8A6', icon: 'life-buoy', gradient: 'from-teal-500 to-emerald-500', badge: 'bg-teal-50 text-teal-700 border-teal-200' },
  'closed': { color: '#64748B', icon: 'check-circle', gradient: 'from-slate-400 to-slate-500', badge: 'bg-slate-100 text-slate-700 border-slate-200' },
}

function getStageColor(stage) {
  if (!stage) return '#3B82F6'
  const key = String(stage).toLowerCase()
  for (const [k, v] of Object.entries(STAGE_CONFIG)) {
    if (key.includes(k)) return v.color
  }
  return '#3B82F6'
}

function getStageIcon(stage) {
  if (!stage) return 'folder-kanban'
  const key = String(stage).toLowerCase()
  for (const [k, v] of Object.entries(STAGE_CONFIG)) {
    if (key.includes(k)) return v.icon
  }
  return 'folder-kanban'
}

function getStageGradient(stage) {
  if (!stage) return 'from-blue-500 to-indigo-500'
  const key = String(stage).toLowerCase()
  for (const [k, v] of Object.entries(STAGE_CONFIG)) {
    if (key.includes(k)) return v.gradient
  }
  return 'from-blue-500 to-indigo-500'
}

function getStageBadgeClasses(stage) {
  if (!stage) return 'bg-blue-50 text-blue-700 border-blue-200'
  const key = String(stage).toLowerCase()
  for (const [k, v] of Object.entries(STAGE_CONFIG)) {
    if (key.includes(k)) return v.badge
  }
  return 'bg-surface-gray-2 text-ink-gray-7 border-outline-gray-2'
}

// Module Meta & Colors
const MODULE_CONFIG = {
  accounts: { color: '#10B981', icon: 'credit-card' },
  buying: { color: '#F59E0B', icon: 'shopping-cart' },
  selling: { color: '#3B82F6', icon: 'trending-up' },
  stock: { color: '#8B5CF6', icon: 'package' },
  hrms: { color: '#EC4899', icon: 'users' },
  crm: { color: '#06B6D4', icon: 'target' },
  manufacturing: { color: '#6366F1', icon: 'cpu' },
  support: { color: '#F97316', icon: 'life-buoy' },
  assets: { color: '#14B8A6', icon: 'server' },
}

function getModuleColor(nameOrCode) {
  if (!nameOrCode) return '#3B82F6'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_CONFIG)) {
    if (key.includes(k)) return v.color
  }
  return '#3B82F6'
}

function getModuleIcon(nameOrCode) {
  if (!nameOrCode) return 'package'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_CONFIG)) {
    if (key.includes(k)) return v.icon
  }
  return 'package'
}

const AVATAR_GRADIENTS = [
  'bg-gradient-to-tr from-blue-500 to-indigo-600',
  'bg-gradient-to-tr from-emerald-500 to-teal-600',
  'bg-gradient-to-tr from-purple-500 to-pink-600',
  'bg-gradient-to-tr from-amber-500 to-orange-600',
  'bg-gradient-to-tr from-cyan-500 to-blue-600',
  'bg-gradient-to-tr from-rose-500 to-red-600',
]

function getClientAvatarGradient(name) {
  if (!name) return AVATAR_GRADIENTS[0]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  const idx = Math.abs(hash) % AVATAR_GRADIENTS.length
  return AVATAR_GRADIENTS[idx]
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
