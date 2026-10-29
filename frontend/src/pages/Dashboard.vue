<template>
  <div class="h-full flex flex-col app-canvas overflow-hidden">
    <!-- Layout Header matching Helpdesk -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-2">
          <h1 class="text-sm font-semibold text-ink-gray-9">Home</h1>
          <Badge theme="gray" variant="subtle" size="sm" label="Portfolio" />
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
    <div class="flex-1 overflow-y-auto p-6 space-y-5">
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
        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Active Projects</span>
            <div class="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shrink-0">
              <Icon name="folder-kanban" size="16" class="text-blue-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ data.kpis?.active_projects || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">Out of {{ data.kpis?.total_projects || 0 }} total</div>
        </div>

        <!-- Overall Portfolio Progress -->
        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Portfolio Progress</span>
            <div class="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center shrink-0">
              <Icon name="trending-up" size="16" class="text-indigo-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ data.kpis?.overall_completion_pct || 0 }}%</div>
          <div class="w-full h-1.5 bg-surface-gray-2 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500 brand-progress"
              :style="{ width: (data.kpis?.overall_completion_pct || 0) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Completed Tasks -->
        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Completed Tasks</span>
            <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-100 flex items-center justify-center shrink-0">
              <Icon name="check-circle" size="16" class="text-emerald-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-emerald-600">{{ data.kpis?.completed_tasks || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">Out of {{ data.kpis?.total_tasks || 0 }} tasks</div>
        </div>

        <!-- Overdue Tasks -->
        <div
          class="p-4 rounded-2xl border shadow-2xs space-y-1.5 transition hover:shadow-xs"
          :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'border-red-200 bg-red-50/20' : 'border-outline-gray-1 bg-surface-white'"
        >
          <div class="flex items-center justify-between text-xs" :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'text-red-700' : 'text-ink-gray-5'">
            <span class="font-medium">Overdue Tasks</span>
            <div
              class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
              :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'bg-red-100 text-red-600 border border-red-200' : 'bg-rose-50 text-rose-500 border border-rose-100'"
            >
              <Icon name="alert-circle" size="16" />
            </div>
          </div>
          <div class="text-2xl font-bold" :class="(data.kpis?.overdue_tasks || 0) > 0 ? 'text-red-600' : 'text-ink-gray-9'">
            {{ data.kpis?.overdue_tasks || 0 }}
          </div>
          <div class="text-[11px] text-ink-gray-4">Requires attention</div>
        </div>

        <!-- Milestones Completed -->
        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Milestones Signed</span>
            <div class="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 border border-amber-100 flex items-center justify-center shrink-0">
              <Icon name="flag" size="16" class="text-amber-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-amber-600">
            {{ data.kpis?.completed_milestones || 0 }} <span class="text-ink-gray-4 text-base font-normal">/ {{ data.kpis?.total_milestones || 0 }}</span>
          </div>
          <div class="text-[11px] text-ink-gray-4">UAT and Go-Live checkpoints</div>
        </div>
      </div>

      <!-- 2. Projects Tracking Table / Portfolio View -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-1 shadow-2xs overflow-hidden">
        <div class="px-5 py-3 border-b border-outline-gray-1 flex items-center justify-between">
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
          <table class="w-full text-left border-collapse">
            <thead class="bg-surface-gray-1 border-b border-outline-gray-1 text-[11px] font-semibold uppercase tracking-wider text-ink-gray-5 select-none">
              <tr>
                <th class="py-2.5 px-4">Project</th>
                <th class="py-2.5 px-3">Stage</th>
                <th class="py-2.5 px-3">Client PoC</th>
                <th class="py-2.5 px-3">Modules in Scope</th>
                <th class="py-2.5 px-3">Completion %</th>
                <th class="py-2.5 px-3">Timeline</th>
                <th class="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1 text-xs">
              <tr v-if="!data.projects || data.projects.length === 0">
                <td colspan="7" class="py-12 text-center text-ink-gray-4">
                  No implementation projects created yet.
                </td>
              </tr>

              <tr
                v-for="p in data.projects"
                :key="p.name"
                @click="$router.push('/projects/' + p.name)"
                class="hover:bg-surface-gray-2 cursor-pointer transition select-none group"
              >
                <!-- Name & Status -->
                <td class="py-3 px-4">
                  <div>
                    <div class="font-medium text-ink-gray-9 group-hover:text-ink-black transition flex items-center gap-1.5">
                      <span>{{ p.project_name }}</span>
                      <Badge
                        v-if="p.is_at_risk"
                        theme="red"
                        variant="subtle"
                        size="sm"
                        label="DELAYED"
                      />
                    </div>
                    <div class="text-[11px] text-ink-gray-4 mt-0.5 font-mono">#{{ p.name }}</div>
                  </div>
                </td>

                <!-- Stage -->
                <td class="py-3 px-3">
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border"
                    :class="getStageBadgeClasses(p.implementation_stage)"
                  >
                    {{ p.implementation_stage || 'Discovery' }}
                  </span>
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
                    <span
                      v-for="m in p.modules"
                      :key="m.module"
                      class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium border transition select-none"
                      :style="{
                        backgroundColor: (m.color || getModuleColor(m.module_name)) + '14',
                        borderColor: (m.color || getModuleColor(m.module_name)) + '30',
                        color: m.color || getModuleColor(m.module_name)
                      }"
                    >
                      <Icon
                        :name="m.icon || getModuleIcon(m.module_name)"
                        size="11"
                        :color="m.color || getModuleColor(m.module_name)"
                      />
                      <span>{{ m.module_name }} {{ m.progress || 0 }}%</span>
                    </span>
                  </div>
                </td>

                <!-- Completion % -->
                <td class="py-3 px-3">
                  <div class="w-28 space-y-1">
                    <div class="flex items-center justify-between text-[11px]">
                      <span class="font-medium text-ink-gray-9">{{ p.percent_complete || 0 }}%</span>
                      <span class="text-ink-gray-4">{{ p.completed_tasks || 0 }}/{{ p.total_tasks || 0 }}</span>
                    </div>
                    <div class="w-full h-1.5 bg-surface-gray-2 rounded-full overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all duration-300"
                        :class="p.percent_complete === 100 ? 'bg-emerald-500' : 'brand-progress'"
                        :style="{ width: (p.percent_complete || 0) + '%' }"
                      ></div>
                    </div>
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

      <!-- 3. Module Health Matrix -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-1 shadow-2xs p-5 space-y-4">
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
            class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white hover:border-outline-gray-2 hover:shadow-xs transition space-y-3"
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
              <span
                class="text-xs font-bold font-mono px-2 py-0.5 rounded-md"
                :style="{
                  backgroundColor: (mod.color || getModuleColor(mod.module_name)) + '15',
                  color: mod.color || getModuleColor(mod.module_name)
                }"
              >
                {{ mod.progress || 0 }}%
              </span>
            </div>

            <!-- Progress bar -->
            <div class="w-full h-1.5 bg-surface-gray-2 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{
                  width: (mod.progress || 0) + '%',
                  backgroundColor: mod.color || getModuleColor(mod.module_name)
                }"
              ></div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-ink-gray-5 pt-0.5">
              <span>{{ mod.completed_tasks || 0 }} of {{ mod.total_tasks || 0 }} tasks</span>
              <span
                v-if="mod.overdue_tasks > 0"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 text-red-600 border border-red-200"
              >
                <Icon name="alert-circle" size="10" />
                <span>{{ mod.overdue_tasks }} overdue</span>
              </span>
              <span v-else class="text-[10px] text-emerald-600 flex items-center gap-1">
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
import Icon from '../components/Icon.vue'
import LayoutHeader from '../components/LayoutHeader.vue'

defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
})

defineEmits(['refresh', 'open-new-project', 'open-new-task', 'select-task'])

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

function getStageBadgeClasses(stage) {
  switch (stage) {
    case 'Discovery':
    case 'Design':
      return 'bg-purple-50 text-purple-700 border-purple-200'
    case 'Configuration & Customization':
    case 'Configuration':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    case 'Data Migration':
      return 'bg-amber-50 text-amber-700 border-amber-200'
    case 'UAT & Training':
      return 'bg-orange-50 text-orange-700 border-orange-200'
    case 'Go-Live':
    case 'Hypercare Support':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    case 'Closed':
      return 'bg-surface-gray-2 text-ink-gray-6 border-outline-gray-2'
    default:
      return 'bg-surface-gray-1 text-ink-gray-7 border-outline-gray-1'
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
