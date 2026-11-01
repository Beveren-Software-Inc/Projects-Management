<template>
  <div class="h-full flex flex-col bg-surface-white overflow-hidden">
    <!-- Layout Header matching Helpdesk -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-2">
          <h1 class="text-sm font-semibold text-ink-gray-9">Dashboard</h1>
          <Badge theme="gray" variant="subtle" size="sm" label="Portfolio Overview" />
        </div>
      </template>

      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            variant="subtle"
            size="sm"
            class="!p-1.5"
            title="Refresh"
            @click="$emit('refresh')"
          >
            <template #prefix>
              <Icon name="refresh" size="13" />
            </template>
          </Button>

          <Button
            variant="subtle"
            size="sm"
            label="New Task"
            @click="$emit('open-new-task')"
          >
            <template #prefix>
              <Icon name="plus" size="13" />
            </template>
          </Button>

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

    <!-- Scrollable Body -->
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- Frappe UI Alert: Overdue Notifications Banner -->
      <Alert
        v-if="(data.kpis?.overdue_tasks || 0) > 0"
        theme="amber"
        title="Overdue Tasks Detected"
        :description="'There are ' + data.kpis.overdue_tasks + ' overdue implementation tasks requiring escalation across active client rollouts.'"
      />

      <!-- 1. KPI Metric Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        <!-- Active Projects -->
        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Active Projects</span>
            <div class="w-9 h-9 rounded-xl bg-surface-blue-2 text-ink-blue-7 flex items-center justify-center shrink-0">
              <Icon name="folder-kanban" size="16" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ data.kpis?.active_projects || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">Out of {{ data.kpis?.total_projects || 0 }} total</div>
        </div>

        <!-- Overall Portfolio Progress -->
        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-2 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Portfolio Progress</span>
            <div class="w-9 h-9 rounded-xl bg-surface-gray-2 text-ink-gray-7 flex items-center justify-center shrink-0">
              <Icon name="trending-up" size="16" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ data.kpis?.overall_completion_pct || 0 }}%</div>
          <Progress :value="data.kpis?.overall_completion_pct || 0" size="sm" />
        </div>

        <!-- Completed Tasks -->
        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Completed Tasks</span>
            <div class="w-9 h-9 rounded-xl bg-surface-green-2 text-ink-green-7 flex items-center justify-center shrink-0">
              <Icon name="check-circle" size="16" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-green-7">{{ data.kpis?.completed_tasks || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">Out of {{ data.kpis?.total_tasks || 0 }} tasks</div>
        </div>

        <!-- Overdue Tasks -->
        <div
          class="p-4 rounded-2xl border shadow-2xs space-y-1.5 transition hover:shadow-xs"
          :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'border-outline-red-3 bg-surface-red-2/30' : 'border-outline-gray-2 bg-surface-white'"
        >
          <div class="flex items-center justify-between text-xs" :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'text-ink-red-7' : 'text-ink-gray-5'">
            <span class="font-medium">Overdue Tasks</span>
            <div
              class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
              :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'bg-surface-red-2 text-ink-red-7' : 'bg-surface-gray-2 text-ink-gray-6'"
            >
              <Icon name="alert-circle" size="16" />
            </div>
          </div>
          <div class="text-2xl font-bold" :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'text-ink-red-7' : 'text-ink-gray-9'">
            {{ data.kpis?.overdue_tasks || 0 }}
          </div>
          <div class="text-[11px] text-ink-gray-4">Requires attention</div>
        </div>

        <!-- Milestones Completed -->
        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Milestones Signed</span>
            <div class="w-9 h-9 rounded-xl bg-surface-amber-2 text-ink-amber-7 flex items-center justify-center shrink-0">
              <Icon name="flag" size="16" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-amber-7">
            {{ data.kpis?.completed_milestones || 0 }} <span class="text-ink-gray-4 text-base font-normal">/ {{ data.kpis?.total_milestones || 0 }}</span>
          </div>
          <div class="text-[11px] text-ink-gray-4">UAT and Go-Live checkpoints</div>
        </div>
      </div>

      <!-- 2. Interactive Charts Row -->
      <div v-if="stageChartData.length || moduleChartData.length" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Donut Chart: Project Stage Distribution -->
        <div class="p-4 bg-surface-white rounded-2xl border border-outline-gray-2 shadow-2xs space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xs font-semibold text-ink-gray-9">Project Stage Distribution</h2>
              <p class="text-[11px] text-ink-gray-5">Rollouts by implementation phase</p>
            </div>
            <Badge theme="blue" variant="subtle" size="sm" :label="(data.projects?.length || 0) + ' Projects'" />
          </div>
          <div class="h-64 flex items-center justify-center">
            <DonutChart
              v-if="stageChartData.length"
              :data="stageChartData"
              category="stage"
              value="count"
              class="w-full h-full"
            />
            <div v-else class="text-xs text-ink-gray-4">No project stage data</div>
          </div>
        </div>

        <!-- Bar Chart: Module Completion Rates -->
        <div class="p-4 bg-surface-white rounded-2xl border border-outline-gray-2 shadow-2xs space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xs font-semibold text-ink-gray-9">Module Task Delivery</h2>
              <p class="text-[11px] text-ink-gray-5">Completed vs remaining tasks by module</p>
            </div>
            <Badge theme="green" variant="subtle" size="sm" label="Task Breakdown" />
          </div>
          <div class="h-64 flex items-center justify-center">
            <BarChart
              v-if="moduleChartData.length"
              :data="moduleChartData"
              x="module"
              :y="['completed', 'open']"
              stacked
              class="w-full h-full"
            />
            <div v-else class="text-xs text-ink-gray-4">No module task data</div>
          </div>
        </div>
      </div>

      <!-- 3. Projects Tracking Table / Portfolio View -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-2 shadow-2xs overflow-hidden">
        <div class="px-5 py-3 border-b border-outline-gray-2 flex items-center justify-between">
          <div>
            <h2 class="text-xs font-semibold text-ink-gray-9">Implementation Projects Tracking</h2>
            <p class="text-[11px] text-ink-gray-5 mt-0.5">Real-time status, module breakdown, stakeholders, and completion percentage.</p>
          </div>
          <router-link to="/projects" class="text-xs text-ink-gray-7 hover:text-ink-gray-9 font-medium flex items-center gap-1">
            <span>View All</span>
            <Icon name="chevron-right" size="12" />
          </router-link>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-surface-gray-1 text-ink-gray-5 font-medium border-b border-outline-gray-2 select-none">
                <th class="py-2.5 px-4">Project</th>
                <th class="py-2.5 px-3">Stage</th>
                <th class="py-2.5 px-3">Client PoC</th>
                <th class="py-2.5 px-3">Modules in Scope</th>
                <th class="py-2.5 px-3">Progress</th>
                <th class="py-2.5 px-3">Timeline</th>
                <th class="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr v-if="!data.projects || data.projects.length === 0">
                <td colspan="7" class="py-12 text-center text-ink-gray-4 text-xs">
                  No active implementation projects found.
                </td>
              </tr>
              <tr
                v-for="p in data.projects"
                :key="p.name"
                class="hover:bg-surface-gray-1/60 transition group cursor-pointer"
                @click="$router.push('/projects/' + p.name)"
              >
                <!-- Project Name & ID -->
                <td class="py-3 px-4">
                  <div class="font-semibold text-ink-gray-9 group-hover:text-ink-blue-7 transition">
                    {{ p.project_name }}
                  </div>
                  <div class="text-[11px] text-ink-gray-4 font-mono">{{ p.name }}</div>
                </td>

                <!-- Stage -->
                <td class="py-3 px-3">
                  <Badge
                    :theme="getStageTheme(p.implementation_stage)"
                    variant="subtle"
                    size="sm"
                    :label="p.implementation_stage || 'Discovery'"
                  />
                </td>

                <!-- Client PoC -->
                <td class="py-3 px-3">
                  <div v-if="p.client_poc_name || p.client_poc_email" class="flex items-center gap-2">
                    <Avatar :label="p.client_poc_name || 'Client'" size="sm" />
                    <div>
                      <div class="font-medium text-ink-gray-8">{{ p.client_poc_name || 'Contact Person' }}</div>
                      <div class="text-[11px] text-ink-gray-4 truncate max-w-xs">{{ p.client_poc_email || '' }}</div>
                    </div>
                  </div>
                  <span v-else class="text-ink-gray-4 italic">No PoC assigned</span>
                </td>

                <!-- Modules in Scope -->
                <td class="py-3 px-3">
                  <div class="flex flex-wrap gap-1.5 max-w-xs">
                    <Badge
                      v-for="m in p.modules"
                      :key="m.module"
                      :theme="getModuleTheme(m.module_name)"
                      variant="subtle"
                      size="sm"
                    >
                      <span class="font-medium">{{ m.module_name }}</span>
                      <span class="ml-1 opacity-80 font-semibold">{{ m.progress || 0 }}%</span>
                    </Badge>
                  </div>
                </td>

                <!-- Completion % -->
                <td class="py-3 px-3">
                  <div class="w-28 space-y-1">
                    <div class="flex items-center justify-between text-[11px]">
                      <span class="font-medium text-ink-gray-9">{{ p.percent_complete || 0 }}%</span>
                      <span class="text-ink-gray-4">{{ p.completed_tasks || 0 }}/{{ p.total_tasks || 0 }}</span>
                    </div>
                    <Progress :value="p.percent_complete || 0" size="sm" />
                  </div>
                </td>

                <!-- Timeline -->
                <td class="py-3 px-3 text-ink-gray-6 text-xs whitespace-nowrap">
                  <div>{{ formatDate(p.expected_start_date) }}</div>
                  <div class="text-[11px] text-ink-gray-4">to {{ formatDate(p.expected_end_date) }}</div>
                </td>

                <!-- Action Link -->
                <td class="py-3 px-4 text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    label="View"
                    @click.stop="$router.push('/projects/' + p.name)"
                  >
                    <template #suffix>
                      <Icon name="chevron-right" size="12" />
                    </template>
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. Module Health Matrix -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-2 shadow-2xs p-5 space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xs font-semibold text-ink-gray-9">Module Implementation Health</h2>
            <p class="text-[11px] text-ink-gray-5 mt-0.5">Aggregate task completion rates across all client projects by ERPNext module.</p>
          </div>
          <router-link to="/modules" class="text-xs text-ink-gray-7 hover:text-ink-gray-9 font-medium flex items-center gap-1">
            <span>Manage Modules</span>
            <Icon name="chevron-right" size="12" />
          </router-link>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
          <div
            v-for="mod in data.modules_health"
            :key="mod.module_code"
            class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white hover:shadow-xs transition space-y-3"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border transition shadow-2xs"
                  :style="{
                    backgroundColor: (mod.color || getModuleColor(mod.module_name)) + '18',
                    borderColor: (mod.color || getModuleColor(mod.module_name)) + '38',
                    color: mod.color || getModuleColor(mod.module_name)
                  }"
                >
                  <Icon
                    :name="mod.icon || getModuleIcon(mod.module_name)"
                    size="18"
                    :color="mod.color || getModuleColor(mod.module_name)"
                  />
                </div>
                <div>
                  <div class="font-semibold text-xs text-ink-gray-9">{{ mod.module_name }}</div>
                  <div class="text-[11px] text-ink-gray-5">{{ mod.active_in_projects || 0 }} {{ mod.active_in_projects === 1 ? 'project' : 'projects' }}</div>
                </div>
              </div>
              <Badge
                theme="gray"
                variant="subtle"
                size="sm"
                :label="(mod.progress || 0) + '%'"
              />
            </div>

            <!-- Progress bar -->
            <Progress :value="mod.progress || 0" size="sm" />

            <div class="flex items-center justify-between text-[11px] text-ink-gray-5 pt-0.5">
              <span>{{ mod.completed_tasks || 0 }} of {{ mod.total_tasks || 0 }} tasks</span>
              <Badge
                v-if="mod.overdue_tasks > 0"
                theme="red"
                variant="subtle"
                size="sm"
                :label="mod.overdue_tasks + ' overdue'"
              />
              <span v-else class="text-[10px] text-ink-green-7 flex items-center gap-1">
                <Icon name="check-circle" size="11" />
                <span>On track</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Button,
  Badge,
  Avatar,
  Progress,
  Alert,
} from 'frappe-ui'
import { DonutChart, BarChart } from 'frappe-ui/charts'
import Icon from '../components/Icon.vue'
import LayoutHeader from '../components/LayoutHeader.vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
})

defineEmits(['refresh', 'open-new-project', 'open-new-task', 'select-task'])

const stageChartData = computed(() => {
  const projects = props.data.projects || []
  if (!projects.length) return []
  const counts = {}
  projects.forEach(p => {
    const stage = p.implementation_stage || 'Discovery'
    counts[stage] = (counts[stage] || 0) + 1
  })
  return Object.entries(counts).map(([stage, count]) => ({
    stage,
    count,
  }))
})

const moduleChartData = computed(() => {
  const modules = props.data.modules_health || []
  if (!modules.length) return []
  return modules.slice(0, 8).map(m => ({
    module: m.module_name,
    completed: m.completed_tasks || 0,
    open: Math.max(0, (m.total_tasks || 0) - (m.completed_tasks || 0)),
  }))
})

const MODULE_META = {
  accounts: { color: '#10B981', icon: 'CreditCard' },
  buying: { color: '#F59E0B', icon: 'ShoppingCart' },
  selling: { color: '#3B82F6', icon: 'TrendingUp' },
  stock: { color: '#8B5CF6', icon: 'Package' },
  hrms: { color: '#EC4899', icon: 'Users' },
  crm: { color: '#06B6D4', icon: 'Target' },
  manufacturing: { color: '#6366F1', icon: 'Cpu' },
  support: { color: '#F97316', icon: 'LifeBuoy' },
  assets: { color: '#14B8A6', icon: 'Server' },
}

function getModuleColor(nameOrCode) {
  if (!nameOrCode) return '#3B82F6'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_META)) {
    if (key.includes(k)) return v.color
  }
  return '#3B82F6'
}

function getModuleIcon(nameOrCode) {
  if (!nameOrCode) return 'package'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_META)) {
    if (key.includes(k)) return v.icon
  }
  return 'package'
}

function getModuleTheme(nameOrCode) {
  if (!nameOrCode) return 'blue'
  const key = String(nameOrCode).toLowerCase()
  if (key.includes('account') || key.includes('finance') || key.includes('asset')) return 'green'
  if (key.includes('sell') || key.includes('order') || key.includes('crm') || key.includes('pipeline')) return 'blue'
  if (key.includes('buy') || key.includes('procure') || key.includes('manufactur')) return 'amber'
  if (key.includes('stock') || key.includes('inventory') || key.includes('support') || key.includes('helpdesk')) return 'violet'
  if (key.includes('hr') || key.includes('payroll') || key.includes('employee')) return 'red'
  return 'blue'
}

function getStageTheme(stage) {
  switch (stage) {
    case 'Discovery':
    case 'Design':
      return 'violet'
    case 'Configuration & Customization':
    case 'Configuration':
      return 'blue'
    case 'Data Migration':
    case 'UAT & Training':
      return 'amber'
    case 'Go-Live':
    case 'Hypercare Support':
      return 'green'
    case 'Closed':
      return 'gray'
    default:
      return 'gray'
  }
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
