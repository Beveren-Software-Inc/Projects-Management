<template>
  <div class="h-full flex flex-col bg-surface-white overflow-hidden">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-2.5">
          <h1 class="text-lg font-semibold text-ink-gray-9">Module Templates</h1>
          <Badge theme="gray" variant="subtle" size="sm" :label="modules.length + ' Modules'" />
        </div>
      </template>

      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            theme="gray"
            variant="solid"
            size="sm"
            label="New Module"
            @click="openCreateModal"
          >
            <template #prefix>
              <Icon name="plus" size="13" />
            </template>
          </Button>

          <Button
            v-if="selectedModule"
            theme="gray"
            variant="subtle"
            size="sm"
            :loading="saving"
            label="Save Template"
            @click="handleSaveTemplate"
          />
        </div>
      </template>
    </LayoutHeader>

    <!-- Main Content Area: Split List & Editor -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left: Module Cards List & Search -->
      <div class="w-80 border-r border-outline-gray-1 bg-surface-white flex flex-col shrink-0 select-none">
        <!-- Search & Quick Action Bar -->
        <div class="p-3 border-b border-outline-gray-1 space-y-2">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search modules..."
              class="w-full pl-8 pr-3 py-1.5 text-sm rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition placeholder:text-ink-gray-4"
            />
            <Icon name="search" size="13" class="absolute left-2.5 top-2.5 text-ink-gray-4" />
          </div>

          <div class="flex items-center justify-between text-xs text-ink-gray-5 px-1">
            <span>{{ filteredModules.length }} modules listed</span>
            <button
              type="button"
              @click="openCreateModal"
              class="text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1 cursor-pointer"
            >
              <Icon name="plus" size="11" />
              <span>Add Module</span>
            </button>
          </div>
        </div>

        <!-- Modules Scroll List -->
        <div class="flex-1 overflow-y-auto p-3 space-y-1.5">
          <div
            v-if="filteredModules.length === 0"
            class="text-center py-8 text-sm text-ink-gray-4 space-y-2"
          >
            <p>No modules match "{{ searchQuery }}"</p>
            <Button
              variant="subtle"
              size="sm"
              label="Create Custom Module"
              @click="openCreateModal"
            />
          </div>

          <div
            v-for="mod in filteredModules"
            :key="mod.module_code"
            @click="selectedModule = mod"
            class="p-2.5 rounded-xl border cursor-pointer transition select-none flex items-center justify-between group"
            :class="selectedModule?.module_code === mod.module_code
              ? 'border-outline-gray-3 bg-surface-gray-2 shadow-2xs'
              : 'border-transparent hover:bg-surface-gray-1'"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <div
                class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border transition"
                :style="{
                  backgroundColor: (mod.color || getModuleColor(mod.module_name)) + '18',
                  borderColor: (mod.color || getModuleColor(mod.module_name)) + '35',
                  color: mod.color || getModuleColor(mod.module_name)
                }"
              >
                <Icon
                  :name="mod.icon || getModuleIcon(mod.module_name)"
                  size="14"
                  :color="mod.color || getModuleColor(mod.module_name)"
                />
              </div>
              <div class="truncate min-w-0">
                <div class="flex items-center gap-1.5 truncate">
                  <h3 class="font-medium text-sm text-ink-gray-9 truncate">{{ mod.module_name }}</h3>
                  <span
                    v-if="isCustomModule(mod)"
                    class="text-[11px] px-1.5 py-0.2 rounded-md bg-blue-50 text-blue-700 border border-blue-200/60 font-medium shrink-0"
                  >
                    Custom
                  </span>
                </div>
                <div class="text-xs text-ink-gray-5">{{ mod.tasks?.length || 0 }} standard tasks</div>
              </div>
            </div>
            <Icon name="chevron-right" size="13" class="text-ink-gray-4 shrink-0 group-hover:text-ink-gray-6 transition" />
          </div>
        </div>
      </div>

      <!-- Right: Task Templates Table -->
      <div class="flex-1 flex flex-col bg-surface-white overflow-hidden">
        <div v-if="!selectedModule" class="flex-1 flex flex-col items-center justify-center p-12 text-center text-sm text-ink-gray-4 space-y-3">
          <div class="w-12 h-12 rounded-2xl bg-surface-gray-2 flex items-center justify-center text-ink-gray-4">
            <Icon name="modules" size="24" />
          </div>
          <div>
            <h3 class="text-sm font-semibold text-ink-gray-8">No Module Selected</h3>
            <p class="text-sm text-ink-gray-5 max-w-sm mt-1">Select a module from the sidebar or click "New Module" to define custom workflows.</p>
          </div>
          <Button
            theme="gray"
            variant="solid"
            size="sm"
            label="Add New Module"
            @click="openCreateModal"
          />
        </div>

        <div v-else class="flex-1 flex flex-col overflow-hidden">
          <!-- Module Sub-header -->
          <div class="px-5 py-3.5 border-b border-outline-gray-1 flex items-center justify-between shrink-0 bg-surface-white">
            <div class="flex items-center gap-3.5 min-w-0">
              <div
                class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 shadow-2xs border"
                :style="{
                  backgroundColor: (selectedModule.color || getModuleColor(selectedModule.module_name)) + '18',
                  borderColor: (selectedModule.color || getModuleColor(selectedModule.module_name)) + '38',
                  color: selectedModule.color || getModuleColor(selectedModule.module_name)
                }"
              >
                <Icon
                  :name="selectedModule.icon || getModuleIcon(selectedModule.module_name)"
                  size="20"
                  :color="selectedModule.color || getModuleColor(selectedModule.module_name)"
                />
              </div>
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <h2 class="font-semibold text-sm text-ink-gray-9 truncate">{{ selectedModule.module_name }}</h2>
                  <span
                    v-if="isCustomModule(selectedModule)"
                    class="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium border border-blue-200/60"
                  >
                    Custom Module
                  </span>
                  <span
                    v-else
                    class="text-xs px-2 py-0.5 rounded-full bg-surface-gray-2 text-ink-gray-6 font-medium"
                  >
                    Standard Module
                  </span>
                </div>
                <p class="text-xs text-ink-gray-5 truncate max-w-xl">
                  {{ selectedModule.description || 'No description provided for this module.' }}
                </p>
              </div>
            </div>

            <!-- Header Actions -->
            <div class="flex items-center gap-2 shrink-0">
              <Button
                variant="subtle"
                size="sm"
                label="Edit Details"
                @click="openEditModal(selectedModule)"
              >
                <template #prefix>
                  <Icon name="edit-2" size="12" />
                </template>
              </Button>

              <Button
                v-if="isCustomModule(selectedModule)"
                variant="subtle"
                size="sm"
                class="!text-red-600 hover:!bg-red-50"
                label="Delete"
                @click="handleDeleteModule(selectedModule)"
              >
                <template #prefix>
                  <Icon name="trash" size="12" />
                </template>
              </Button>

              <Button
                variant="subtle"
                size="sm"
                label="Add Template Task"
                @click="handleAddTask"
              >
                <template #prefix>
                  <Icon name="plus" size="13" />
                </template>
              </Button>
            </div>
          </div>

          <!-- Tasks Table -->
          <div class="flex-1 overflow-auto">
            <table class="w-full text-left border-collapse">
              <thead class="bg-surface-gray-1 border-b border-outline-gray-1 text-xs font-semibold text-ink-gray-5 uppercase tracking-wider sticky top-0 z-10 select-none">
                <tr>
                  <th class="py-2.5 px-4 w-12 text-center">#</th>
                  <th class="py-2.5 px-3">Task Subject</th>
                  <th class="py-2.5 px-3 w-28">Priority</th>
                  <th class="py-2.5 px-3 w-24">Offset (Days)</th>
                  <th class="py-2.5 px-3 w-24">Duration</th>
                  <th class="py-2.5 px-3 w-20 text-center">Milestone</th>
                  <th class="py-2.5 px-4 w-12 text-right"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1 text-sm">
                <tr v-if="!selectedModule.tasks || selectedModule.tasks.length === 0">
                  <td colspan="7" class="py-12 text-center text-ink-gray-4">
                    No task templates defined. Click "Add Template Task" to create one.
                  </td>
                </tr>

                <tr
                  v-for="(task, idx) in selectedModule.tasks"
                  :key="idx"
                  class="hover:bg-surface-gray-1 transition"
                >
                  <td class="py-2.5 px-4 text-center text-xs font-mono text-ink-gray-4">{{ idx + 1 }}</td>
                  <td class="py-2.5 px-3">
                    <input
                      v-model="task.subject"
                      type="text"
                      class="w-full px-2.5 py-1 text-sm rounded-xl border border-transparent hover:border-outline-gray-2 focus:border-outline-gray-3 bg-transparent focus:bg-white text-ink-gray-9 focus:outline-none transition"
                    />
                  </td>
                  <td class="py-2.5 px-3">
                    <select
                      v-model="task.priority"
                      class="px-2.5 py-1 text-sm rounded-xl border border-outline-gray-2 bg-white text-ink-gray-8 focus:outline-none transition cursor-pointer"
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                      <option value="Urgent">Urgent</option>
                    </select>
                  </td>
                  <td class="py-2.5 px-3">
                    <input
                      v-model.number="task.day_offset"
                      type="number"
                      min="0"
                      class="w-16 px-2.5 py-1 text-sm rounded-xl border border-outline-gray-2 text-ink-gray-8 focus:outline-none transition"
                    />
                  </td>
                  <td class="py-2.5 px-3">
                    <input
                      v-model.number="task.duration_days"
                      type="number"
                      min="1"
                      class="w-16 px-2.5 py-1 text-sm rounded-xl border border-outline-gray-2 text-ink-gray-8 focus:outline-none transition"
                    />
                  </td>
                  <td class="py-2.5 px-3 text-center">
                    <input
                      v-model="task.is_milestone"
                      type="checkbox"
                      class="rounded-md border-outline-gray-3 text-ink-gray-9 focus:ring-0 cursor-pointer"
                    />
                  </td>
                  <td class="py-2.5 px-4 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      class="!p-1 text-ink-gray-4 hover:text-red-600 rounded-lg cursor-pointer"
                      title="Remove"
                      @click="removeTask(idx)"
                    >
                      <template #prefix>
                        <Icon name="trash" size="13" />
                      </template>
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- New / Edit Module Modal -->
    <NewModuleModal
      :show="showModal"
      :module-data="modalModuleData"
      @close="closeModal"
      @saved="onModuleSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, Badge, toast } from 'frappe-ui'
import Icon from '../components/Icon.vue'
import LayoutHeader from '../components/LayoutHeader.vue'
import NewModuleModal from '../components/NewModuleModal.vue'
import {
  getImplementationModules,
  saveModuleTemplate,
  deleteImplementationModule,
} from '../api'

const modules = ref([])
const selectedModule = ref(null)
const saving = ref(false)
const searchQuery = ref('')

const showModal = ref(false)
const modalModuleData = ref(null)

const STANDARD_CODES = [
  'accounts',
  'buying',
  'selling',
  'stock',
  'hrms',
  'crm',
  'manufacturing',
  'support',
  'assets',
]

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

function isCustomModule(mod) {
  if (!mod?.module_code) return false
  return !STANDARD_CODES.includes(mod.module_code)
}

const filteredModules = computed(() => {
  if (!searchQuery.value.trim()) return modules.value
  const q = searchQuery.value.toLowerCase()
  return modules.value.filter(
    m =>
      (m.module_name || '').toLowerCase().includes(q) ||
      (m.module_code || '').toLowerCase().includes(q) ||
      (m.description || '').toLowerCase().includes(q)
  )
})

function getModuleColor(nameOrCode) {
  if (!nameOrCode) return '#3B82F6'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_META)) {
    if (key.includes(k)) return v.color
  }
  return '#3B82F6'
}

function getModuleIcon(nameOrCode) {
  if (!nameOrCode) return 'Package'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_META)) {
    if (key.includes(k)) return v.icon
  }
  return 'Package'
}

onMounted(async () => {
  await loadModules()
})

async function loadModules(selectCode = null) {
  try {
    const list = await getImplementationModules()
    modules.value = list || []
    if (selectCode) {
      selectedModule.value = modules.value.find(m => m.module_code === selectCode) || modules.value[0]
    } else if (!selectedModule.value && modules.value.length > 0) {
      selectedModule.value = modules.value[0]
    } else if (selectedModule.value) {
      // Refresh current selected module data
      const updated = modules.value.find(m => m.module_code === selectedModule.value.module_code)
      if (updated) selectedModule.value = updated
    }
  } catch (e) {
    console.error('Failed to load modules:', e)
  }
}

function openCreateModal() {
  modalModuleData.value = null
  showModal.value = true
}

function openEditModal(mod) {
  modalModuleData.value = { ...mod }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  modalModuleData.value = null
}

async function onModuleSaved(moduleCode) {
  await loadModules(moduleCode)
}

async function handleDeleteModule(mod) {
  if (!confirm(`Are you sure you want to delete module "${mod.module_name}" and its task templates?`)) {
    return
  }
  try {
    const list = await deleteImplementationModule(mod.module_code)
    modules.value = list || []
    selectedModule.value = modules.value.length > 0 ? modules.value[0] : null
    toast.success('Module deleted successfully')
  } catch (e) {
    toast.error('Failed to delete module: ' + (e.message || e))
  }
}

function handleAddTask() {
  if (!selectedModule.value) return
  if (!selectedModule.value.tasks) selectedModule.value.tasks = []
  selectedModule.value.tasks.push({
    subject: 'New Implementation Task',
    description: '',
    day_offset: 5,
    duration_days: 3,
    expected_hours: 8,
    priority: 'Medium',
    is_milestone: 0,
  })
}

function removeTask(idx) {
  if (!selectedModule.value?.tasks) return
  selectedModule.value.tasks.splice(idx, 1)
}

async function handleSaveTemplate() {
  if (!selectedModule.value) return
  saving.value = true
  try {
    await saveModuleTemplate(selectedModule.value.module_code, {
      tasks: selectedModule.value.tasks,
    })
    toast.success('Template saved successfully!')
    await loadModules(selectedModule.value.module_code)
  } catch (e) {
    toast.error('Failed to save template: ' + (e.message || e))
  } finally {
    saving.value = false
  }
}
</script>
