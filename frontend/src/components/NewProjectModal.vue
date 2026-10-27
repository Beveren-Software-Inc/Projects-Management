<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl border border-outline-gray-2 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-outline-gray-2 flex items-center justify-between shrink-0 bg-white rounded-t-2xl">
        <div>
          <h2 class="text-base font-semibold text-ink-gray-9">Create Implementation Project</h2>
          <p class="text-xs text-ink-gray-5 mt-0.5">Configure project details and select modules to automatically generate implementation tasks.</p>
        </div>
        <button
          @click="$emit('close')"
          class="p-1.5 text-ink-gray-4 hover:text-ink-gray-7 rounded-xl hover:bg-surface-gray-2 transition"
        >
          <Icon name="x" size="18" />
        </button>
      </div>

      <!-- Modal Body (Tabs / Steps) -->
      <div class="flex border-b border-outline-gray-2 px-6 bg-surface-gray-1 shrink-0">
        <button
          type="button"
          @click="activeTab = 'details'"
          class="py-2.5 px-4 text-xs font-medium border-b-2 transition"
          :class="activeTab === 'details' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          1. Project Details & Stakeholders
        </button>
        <button
          type="button"
          @click="activeTab = 'modules'"
          class="py-2.5 px-4 text-xs font-medium border-b-2 transition flex items-center gap-1.5"
          :class="activeTab === 'modules' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          <span>2. Select Modules</span>
          <Badge theme="blue" variant="subtle" size="sm" :label="selectedModules.length + ' selected'" />
        </button>
        <button
          type="button"
          @click="activeTab = 'preview'"
          class="py-2.5 px-4 text-xs font-medium border-b-2 transition flex items-center gap-1.5"
          :class="activeTab === 'preview' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          <span>3. Task Preview</span>
          <Badge theme="gray" variant="subtle" size="sm" :label="totalPreviewTasks + ' tasks'" />
        </button>
      </div>

      <!-- Tab Content (Scrollable) -->
      <div class="p-6 overflow-y-auto flex-1 bg-white">
        
        <!-- TAB 1: DETAILS -->
        <div v-show="activeTab === 'details'" class="space-y-5">
          <!-- Project General -->
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2 sm:col-span-1">
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Project Name <span class="text-red-500">*</span></label>
              <input
                v-model="form.project_name"
                type="text"
                placeholder="e.g. Acme Corp ERPNext Rollout"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
                required
              />
            </div>
            <div class="col-span-2 sm:col-span-1">
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Project Type</label>
              <input
                v-model="form.project_type"
                type="text"
                placeholder="Implementation"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
              />
            </div>
          </div>

          <!-- Dates & Priority -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Expected Start Date</label>
              <input
                v-model="form.expected_start_date"
                type="date"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Expected End Date</label>
              <input
                v-model="form.expected_end_date"
                type="date"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Priority</label>
              <select
                v-model="form.priority"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs cursor-pointer"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
              </select>
            </div>
          </div>

          <!-- Client Details Section -->
          <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-gray-1 space-y-3">
            <div class="text-xs font-semibold text-ink-gray-8 flex items-center gap-1.5">
              <div class="w-6 h-6 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <Icon name="user" size="13" />
              </div>
              <span>Client's Point of Contact (PoC)</span>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-[11px] font-medium text-ink-gray-6 mb-1">Contact Name</label>
                <input
                  v-model="form.client_poc_name"
                  type="text"
                  placeholder="e.g. John Doe"
                  class="w-full px-3 py-1.5 text-xs rounded-xl border border-outline-gray-3 bg-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-[11px] font-medium text-ink-gray-6 mb-1">Contact Email (for auto updates)</label>
                <input
                  v-model="form.client_poc_email"
                  type="email"
                  placeholder="john@clientcorp.com"
                  class="w-full px-3 py-1.5 text-xs rounded-xl border border-outline-gray-3 bg-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-[11px] font-medium text-ink-gray-6 mb-1">Contact Phone</label>
                <input
                  v-model="form.client_poc_phone"
                  type="text"
                  placeholder="+1 555-0199"
                  class="w-full px-3 py-1.5 text-xs rounded-xl border border-outline-gray-3 bg-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <!-- Auto Email Checkbox -->
            <label class="flex items-center gap-2 cursor-pointer pt-1">
              <input
                v-model="form.auto_emails"
                type="checkbox"
                class="rounded-md text-blue-600 focus:ring-blue-500"
              />
              <span class="text-xs text-ink-gray-7">Send automated kickoff email and milestone notifications to Client PoC</span>
            </label>
          </div>

          <!-- Partner PoC & Project Manager -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Partner Side PoC</label>
              <select
                v-model="form.partner_poc"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-3 focus:outline-none focus:border-blue-500"
              >
                <option value="">-- Select Partner PoC --</option>
                <option v-for="u in users" :key="u.name" :value="u.name">
                  {{ u.full_name || u.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Project Manager</label>
              <select
                v-model="form.project_manager"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-3 focus:outline-none focus:border-blue-500"
              >
                <option value="">-- Select Project Manager --</option>
                <option v-for="u in users" :key="u.name" :value="u.name">
                  {{ u.full_name || u.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Tags & Stage -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Implementation Stage</label>
              <select
                v-model="form.implementation_stage"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-3 focus:outline-none focus:border-blue-500"
              >
                <option value="Discovery">Discovery & Requirement Gathering</option>
                <option value="Design">Solution Design & Architecture</option>
                <option value="Configuration & Customization">Configuration & Customization</option>
                <option value="Data Migration">Data Cleansing & Migration</option>
                <option value="UAT & Training">UAT & User Training</option>
                <option value="Go-Live">Go-Live Execution</option>
                <option value="Hypercare Support">Hypercare Support</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Tags (comma separated)</label>
              <input
                v-model="tagsInput"
                type="text"
                placeholder="Enterprise, Retail, High-Priority"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-3 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        <!-- TAB 2: SELECT MODULES -->
        <div v-show="activeTab === 'modules'" class="space-y-4">
          <Alert
            theme="blue"
            title="Automated Task Instantiation"
            description="Each selected module will automatically generate standard implementation tasks, milestones, and work breakdown structures for this rollout."
          />

          <div class="flex items-center justify-between">
            <div class="text-xs text-ink-gray-6">
              Select which ERPNext modules are in scope for this client:
            </div>
            <div class="flex gap-2">
              <button
                type="button"
                @click="selectAllModules"
                class="text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                Select All
              </button>
              <span class="text-outline-gray-4">|</span>
              <button
                type="button"
                @click="deselectAllModules"
                class="text-xs text-ink-gray-5 hover:text-ink-gray-7 font-medium"
              >
                Clear
              </button>
            </div>
          </div>

          <!-- Modules Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="mod in availableModules"
              :key="mod.module_code"
              @click="toggleModule(mod.module_code)"
              class="relative p-3.5 rounded-2xl border cursor-pointer transition select-none flex flex-col justify-between"
              :class="isModuleSelected(mod.module_code)
                ? 'border-blue-600 bg-blue-50/40 shadow-xs'
                : 'border-outline-gray-2 bg-surface-white hover:border-outline-gray-4 hover:shadow-xs'"
            >
              <div>
                <div class="flex items-start justify-between mb-2">
                  <div
                    class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                    :style="{ backgroundColor: (mod.color || '#3B82F6') + '20', color: mod.color || '#3B82F6' }"
                  >
                    <Icon :name="mod.icon || 'package'" size="17" />
                  </div>
                  <div
                    class="w-4 h-4 rounded-md border flex items-center justify-center transition"
                    :class="isModuleSelected(mod.module_code)
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'border-outline-gray-3 bg-white'"
                  >
                    <Icon v-if="isModuleSelected(mod.module_code)" name="check-circle" size="12" />
                  </div>
                </div>

                <div class="font-semibold text-xs text-ink-gray-9 mb-1">{{ mod.module_name }}</div>
                <p class="text-[11px] text-ink-gray-5 line-clamp-2 leading-relaxed">{{ mod.description }}</p>
              </div>

              <div class="mt-3 pt-2 border-t border-outline-gray-2/60 flex items-center justify-between text-[11px] text-ink-gray-5">
                <span>{{ mod.task_count || mod.tasks?.length || 0 }} standard tasks</span>
                <span v-if="isModuleSelected(mod.module_code)" class="text-blue-600 font-medium">Included</span>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 3: TASK PREVIEW -->
        <div v-show="activeTab === 'preview'" class="space-y-4">
          <div class="p-3 bg-blue-50 rounded-xl border border-blue-100 flex items-center justify-between text-xs text-blue-900">
            <span>
              Total <b>{{ totalPreviewTasks }} tasks</b> will be generated starting from <b>{{ form.expected_start_date }}</b>.
            </span>
            <span class="text-[11px] text-blue-700">Calculated based on module lead days</span>
          </div>

          <div v-if="previewModules.length === 0" class="py-12 text-center text-xs text-ink-gray-5">
            No modules selected. Please go to "2. Select Modules" and pick at least one module.
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="mod in previewModules"
              :key="mod.module_code"
              class="border border-outline-gray-2 rounded-2xl overflow-hidden bg-white shadow-xs"
            >
              <div
                class="px-4 py-2.5 bg-surface-gray-1 border-b border-outline-gray-2 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <div
                    class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                    :style="{ backgroundColor: (mod.color || '#3B82F6') + '20', color: mod.color || '#3B82F6' }"
                  >
                    <Icon :name="mod.icon || 'package'" size="14" />
                  </div>
                  <span class="text-xs font-semibold text-ink-gray-9">{{ mod.module_name }}</span>
                </div>
                <span class="text-[11px] text-ink-gray-5 font-medium">{{ mod.tasks?.length || 0 }} tasks</span>
              </div>

              <div class="divide-y divide-outline-gray-1">
                <div
                  v-for="(task, idx) in mod.tasks"
                  :key="idx"
                  class="px-4 py-2 flex items-center justify-between text-xs hover:bg-surface-gray-1/50 transition"
                >
                  <div class="flex items-center gap-2.5">
                    <span class="text-[11px] text-ink-gray-4 font-mono w-4">{{ idx + 1 }}</span>
                    <div>
                      <div class="font-medium text-ink-gray-8">{{ task.subject }}</div>
                      <div class="text-[11px] text-ink-gray-5 line-clamp-1">{{ task.description }}</div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <span
                      v-if="task.is_milestone"
                      class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800"
                    >
                      Milestone
                    </span>
                    <span
                      class="px-1.5 py-0.5 rounded text-[10px] font-medium"
                      :class="task.priority === 'High' || task.priority === 'Urgent' ? 'bg-red-50 text-red-600' : 'bg-surface-gray-2 text-ink-gray-6'"
                    >
                      {{ task.priority || 'Medium' }}
                    </span>
                    <span class="text-[11px] text-ink-gray-5 font-mono">+{{ task.day_offset }}d</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-3.5 border-t border-outline-gray-2 flex items-center justify-between shrink-0 bg-white rounded-b-2xl">
        <div>
          <Button
            v-if="activeTab !== 'details'"
            variant="ghost"
            size="sm"
            class="rounded-xl"
            label="← Back"
            @click="activeTab = activeTab === 'preview' ? 'modules' : 'details'"
          />
        </div>

        <div class="flex items-center gap-2">
          <Button
            variant="subtle"
            size="sm"
            class="rounded-xl"
            label="Cancel"
            @click="$emit('close')"
          />

          <Button
            v-if="activeTab !== 'preview'"
            theme="gray"
            variant="solid"
            size="sm"
            class="rounded-xl"
            label="Next Step →"
            @click="activeTab = activeTab === 'details' ? 'modules' : 'preview'"
          />

          <Button
            v-else
            theme="gray"
            variant="solid"
            size="sm"
            class="rounded-xl"
            :disabled="loading || !form.project_name || selectedModules.length === 0"
            :loading="loading"
            label="Create Project & Instantiate Tasks"
            @click="handleSubmit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Icon from './Icon.vue'
import { createProject, getImplementationModules, getUsers } from '../api'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'created'])

const activeTab = ref('details')
const loading = ref(false)
const availableModules = ref([])
const selectedModules = ref(['accounts', 'buying', 'selling', 'stock'])
const users = ref([])
const tagsInput = ref('')

const todayDate = new Date().toISOString().split('T')[0]
const futureDate = new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

const form = ref({
  project_name: '',
  project_type: 'Implementation',
  expected_start_date: todayDate,
  expected_end_date: futureDate,
  priority: 'Medium',
  client_poc_name: '',
  client_poc_email: '',
  client_poc_phone: '',
  partner_poc: '',
  project_manager: '',
  implementation_stage: 'Discovery',
  auto_emails: true,
})

onMounted(async () => {
  try {
    const [mods, uList] = await Promise.all([
      getImplementationModules(),
      getUsers(),
    ])
    availableModules.value = mods || []
    users.value = uList || []
  } catch (e) {
    console.error('Failed to load initial modal data', e)
  }
})

function toggleModule(code) {
  if (selectedModules.value.includes(code)) {
    selectedModules.value = selectedModules.value.filter(c => c !== code)
  } else {
    selectedModules.value.push(code)
  }
}

function isModuleSelected(code) {
  return selectedModules.value.includes(code)
}

function selectAllModules() {
  selectedModules.value = availableModules.value.map(m => m.module_code)
}

function deselectAllModules() {
  selectedModules.value = []
}

const previewModules = computed(() => {
  return availableModules.value.filter(m => selectedModules.value.includes(m.module_code))
})

const totalPreviewTasks = computed(() => {
  return previewModules.value.reduce((acc, m) => acc + (m.tasks?.length || 0), 0)
})

async function handleSubmit() {
  if (!form.value.project_name) {
    activeTab.value = 'details'
    return
  }
  if (selectedModules.value.length === 0) {
    activeTab.value = 'modules'
    return
  }

  loading.value = true
  try {
    const tags = tagsInput.value
      ? tagsInput.value.split(',').map(t => t.trim()).filter(Boolean)
      : []

    const payload = {
      ...form.value,
      selected_modules: selectedModules.value,
      tags,
    }

    const res = await createProject(payload)
    emit('created', res)
    emit('close')
  } catch (e) {
    alert('Error creating project: ' + e.message)
  } finally {
    loading.value = false
  }
}
</script>

