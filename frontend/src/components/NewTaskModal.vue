<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl border border-outline-gray-2 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Header -->
      <div class="px-5 py-3.5 border-b border-outline-gray-2 flex items-center justify-between bg-white rounded-t-2xl">
        <h2 class="text-sm font-semibold text-ink-gray-9">Create New Task</h2>
        <button
          @click="$emit('close')"
          class="p-1.5 text-ink-gray-4 hover:text-ink-gray-7 rounded-xl hover:bg-surface-gray-2 transition"
        >
          <Icon name="x" size="16" />
        </button>
      </div>

      <!-- Form Body -->
      <form @submit.prevent="handleSubmit" class="p-5 space-y-4 bg-white rounded-b-2xl">
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Subject <span class="text-red-500">*</span></label>
          <input
            v-model="form.subject"
            type="text"
            placeholder="e.g. Chart of Accounts Configuration"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
            required
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Project <span class="text-red-500">*</span></label>
            <select
              v-model="form.project"
              class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs cursor-pointer"
              required
            >
              <option value="">-- Select Project --</option>
              <option v-for="p in projects" :key="p.name" :value="p.name">
                {{ p.project_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Implementation Module</label>
            <select
              v-model="form.implementation_module"
              class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs cursor-pointer"
            >
              <option value="">-- Select Module --</option>
              <option v-for="m in modules" :key="m.module_code" :value="m.module_code">
                {{ m.module_name }}
              </option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3">
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
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Start Date</label>
            <input
              v-model="form.exp_start_date"
              type="date"
              @change="onStartDateChange"
              class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">Due Date</label>
            <input
              v-model="form.exp_end_date"
              type="date"
              :min="form.exp_start_date"
              class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Assign User</label>
          <select
            v-model="selectedAssignee"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs cursor-pointer"
          >
            <option value="">-- Unassigned --</option>
            <option v-for="u in users" :key="u.name" :value="u.name">
              {{ u.full_name || u.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Description / Checklist</label>
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="Detailed instructions or acceptance criteria..."
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
          ></textarea>
        </div>

        <div class="flex items-center gap-4 pt-1">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_milestone" type="checkbox" class="rounded text-blue-600 focus:ring-blue-500" />
            <span class="text-xs text-ink-gray-7">Mark as Key Milestone</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.client_visible" type="checkbox" class="rounded text-blue-600 focus:ring-blue-500" />
            <span class="text-xs text-ink-gray-7">Visible to Client</span>
          </label>
        </div>

        <!-- Footer -->
        <div class="pt-3 border-t border-outline-gray-2 flex items-center justify-end gap-2">
          <Button
            variant="subtle"
            size="sm"
            class="rounded-xl"
            label="Cancel"
            @click="$emit('close')"
          />
          <Button
            theme="gray"
            variant="solid"
            size="sm"
            class="rounded-xl"
            :loading="loading"
            label="Create Task"
            type="submit"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Icon from './Icon.vue'
import { createTask, getProjects, getImplementationModules, getUsers } from '../api'

const props = defineProps({
  show: Boolean,
  initialProject: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['close', 'created'])

const loading = ref(false)
const projects = ref([])
const modules = ref([])
const users = ref([])
const selectedAssignee = ref('')

const todayDate = new Date().toISOString().split('T')[0]
const nextWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

const form = ref({
  subject: '',
  project: props.initialProject || '',
  implementation_module: '',
  priority: 'Medium',
  exp_start_date: todayDate,
  exp_end_date: nextWeek,
  description: '',
  is_milestone: false,
  client_visible: true,
})

onMounted(async () => {
  try {
    const [pList, mList, uList] = await Promise.all([
      getProjects(),
      getImplementationModules(),
      getUsers(),
    ])
    projects.value = pList || []
    modules.value = mList || []
    users.value = uList || []
    if (props.initialProject) {
      form.value.project = props.initialProject
    }
  } catch (e) {
    console.error(e)
  }
})

function onStartDateChange() {
  if (form.value.exp_start_date && form.value.exp_end_date) {
    if (form.value.exp_end_date < form.value.exp_start_date) {
      form.value.exp_end_date = form.value.exp_start_date
    }
  }
}

async function handleSubmit() {
  if (!form.value.subject || !form.value.project) return

  if (form.value.exp_start_date && form.value.exp_end_date) {
    if (form.value.exp_end_date < form.value.exp_start_date) {
      form.value.exp_end_date = form.value.exp_start_date
    }
  }

  loading.value = true
  try {
    const payload = {
      ...form.value,
      assignees: selectedAssignee.value ? [selectedAssignee.value] : [],
    }
    const res = await createTask(payload)
    emit('created', res)
    emit('close')
  } catch (e) {
    alert(e.message || 'Error creating task')
  } finally {
    loading.value = false
  }
}
</script>

