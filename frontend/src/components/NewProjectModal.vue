<template>
  <Dialog
    :model-value="show"
    @update:model-value="$emit('close')"
    size="4xl"
  >
    <!-- Custom Header Slot -->
    <template #title>
      <div class="flex items-center justify-between w-full">
        <div>
          <h2 class="text-base font-semibold text-ink-gray-9">Create Implementation Project</h2>
          <p class="text-xs text-ink-gray-5 mt-0.5">Configure project details and select modules to automatically generate implementation tasks.</p>
        </div>
      </div>
    </template>

    <!-- Body Content -->
    <div class="space-y-4 pt-1">
      <!-- Steps Navigation using TabButtons -->
      <TabButtons
        :buttons="[
          { label: '1. Project Details', value: 'details' },
          { label: `2. Select Modules (${selectedModules.length})`, value: 'modules' },
          { label: `3. Task Preview (${totalPreviewTasks})`, value: 'preview' },
        ]"
        v-model="activeTab"
        class="w-full"
      />

      <!-- TAB 1: DETAILS -->
      <div v-show="activeTab === 'details'" class="space-y-4 pt-2 max-h-[60vh] overflow-y-auto px-1">
        <!-- Project General -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <TextInput
            v-model="form.project_name"
            label="Project Name *"
            placeholder="e.g. Acme Corp ERPNext Rollout"
            size="sm"
            required
          />
          <TextInput
            v-model="form.project_type"
            label="Project Type"
            placeholder="Implementation"
            size="sm"
          />
        </div>

        <!-- Dates & Priority -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <TextInput
            v-model="form.expected_start_date"
            type="date"
            label="Expected Start Date"
            size="sm"
          />
          <TextInput
            v-model="form.expected_end_date"
            type="date"
            label="Expected End Date"
            size="sm"
          />
          <Select
            v-model="form.priority"
            label="Priority"
            :options="[
              { label: 'Low', value: 'Low' },
              { label: 'Medium', value: 'Medium' },
              { label: 'High', value: 'High' },
              { label: 'Urgent', value: 'Urgent' },
            ]"
            size="sm"
          />
        </div>

        <!-- Client Details Section -->
        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-gray-1 space-y-3">
          <div class="text-xs font-semibold text-ink-gray-8 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-surface-blue-2 text-ink-blue-7 flex items-center justify-center shrink-0">
              <Icon name="user" size="13" />
            </div>
            <span>Client Point of Contact (PoC)</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <TextInput
              v-model="form.client_poc_name"
              label="Contact Name"
              placeholder="e.g. John Doe"
              size="sm"
            />
            <TextInput
              v-model="form.client_poc_email"
              type="email"
              label="Contact Email"
              placeholder="john@clientcorp.com"
              size="sm"
            />
            <TextInput
              v-model="form.client_poc_phone"
              label="Contact Phone"
              placeholder="+1 555-0199"
              size="sm"
            />
          </div>

          <div class="pt-1">
            <Checkbox
              v-model="form.auto_emails"
              label="Send automated kickoff email and milestone notifications to Client PoC"
            />
          </div>
        </div>

        <!-- Partner PoC & Project Manager -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Select
            v-model="form.partner_poc"
            label="Partner Side PoC"
            placeholder="Select Partner PoC"
            :options="userOptions"
            size="sm"
          />
          <Select
            v-model="form.project_manager"
            label="Project Manager"
            placeholder="Select Project Manager"
            :options="userOptions"
            size="sm"
          />
        </div>

        <!-- Tags & Stage -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Select
            v-model="form.implementation_stage"
            label="Implementation Stage"
            :options="[
              { label: 'Discovery & Requirement Gathering', value: 'Discovery' },
              { label: 'Solution Design & Architecture', value: 'Design' },
              { label: 'Configuration & Customization', value: 'Configuration & Customization' },
              { label: 'Data Cleansing & Migration', value: 'Data Migration' },
              { label: 'UAT & User Training', value: 'UAT & Training' },
              { label: 'Go-Live Execution', value: 'Go-Live' },
              { label: 'Hypercare Support', value: 'Hypercare Support' },
              { label: 'Closed', value: 'Closed' },
            ]"
            size="sm"
          />
          <TextInput
            v-model="tagsInput"
            label="Tags (comma separated)"
            placeholder="Enterprise, Retail, High-Priority"
            size="sm"
          />
        </div>
      </div>

      <!-- TAB 2: SELECT MODULES -->
      <div v-show="activeTab === 'modules'" class="space-y-4 pt-2 max-h-[60vh] overflow-y-auto px-1">
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
            <Button
              variant="ghost"
              size="sm"
              label="Select All"
              @click="selectAllModules"
            />
            <Button
              variant="ghost"
              size="sm"
              label="Clear"
              @click="deselectAllModules"
            />
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
              ? 'border-blue-600 bg-surface-blue-2/30 shadow-xs'
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
                    ? 'bg-surface-blue-7 border-surface-blue-7 text-white'
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
              <Badge
                v-if="isModuleSelected(mod.module_code)"
                theme="blue"
                variant="subtle"
                size="sm"
                label="Included"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 3: TASK PREVIEW -->
      <div v-show="activeTab === 'preview'" class="space-y-4 pt-2 max-h-[60vh] overflow-y-auto px-1">
        <div class="p-3 bg-surface-blue-2 rounded-xl border border-outline-blue-3 flex items-center justify-between text-xs text-ink-blue-7">
          <span>
            Total <b>{{ totalPreviewTasks }} tasks</b> will be generated starting from <b>{{ form.expected_start_date }}</b>.
          </span>
          <span class="text-[11px]">Calculated based on module lead days</span>
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
              <Badge theme="gray" variant="subtle" size="sm" :label="(mod.tasks?.length || 0) + ' tasks'" />
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
                  <Badge
                    v-if="task.is_milestone"
                    theme="amber"
                    variant="subtle"
                    size="sm"
                    label="Milestone"
                  />
                  <Badge
                    :theme="task.priority === 'High' || task.priority === 'Urgent' ? 'red' : 'gray'"
                    variant="subtle"
                    size="sm"
                    :label="task.priority || 'Medium'"
                  />
                  <span class="text-[11px] text-ink-gray-5 font-mono">+{{ task.day_offset }}d</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions Footer Slot -->
    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div>
          <Button
            v-if="activeTab !== 'details'"
            variant="ghost"
            size="sm"
            label="← Back"
            @click="activeTab = activeTab === 'preview' ? 'modules' : 'details'"
          />
        </div>

        <div class="flex items-center gap-2">
          <Button
            variant="subtle"
            size="sm"
            label="Cancel"
            @click="$emit('close')"
          />

          <Button
            v-if="activeTab !== 'preview'"
            theme="gray"
            variant="solid"
            size="sm"
            label="Next Step →"
            @click="activeTab = activeTab === 'details' ? 'modules' : 'preview'"
          />

          <Button
            v-else
            theme="gray"
            variant="solid"
            size="sm"
            :disabled="loading || !form.project_name || selectedModules.length === 0"
            :loading="loading"
            label="Create Project & Instantiate Tasks"
            @click="handleSubmit"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Dialog,
  Button,
  Badge,
  Alert,
  TextInput,
  Select,
  Checkbox,
  TabButtons,
  toast,
} from 'frappe-ui'
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

const userOptions = computed(() => {
  return [
    { label: '-- Select User --', value: '' },
    ...users.value.map(u => ({
      label: u.full_name || u.name,
      value: u.name,
    })),
  ]
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
    toast.error('Please enter a project name')
    return
  }
  if (selectedModules.value.length === 0) {
    activeTab.value = 'modules'
    toast.error('Please select at least one module')
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
    toast.success('Project created successfully with implementation tasks!')
    emit('created', res)
    emit('close')
  } catch (e) {
    toast.error('Error creating project: ' + (e.message || e))
  } finally {
    loading.value = false
  }
}
</script>
