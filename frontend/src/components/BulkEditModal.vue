<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 select-none"
    @click.self="$emit('close')"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl border border-outline-gray-2 w-full max-w-lg overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-outline-gray-2 flex items-center justify-between bg-white rounded-t-2xl shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-surface-gray-2 border border-outline-gray-2 flex items-center justify-center text-ink-gray-7">
            <Icon name="check-square" size="18" />
          </div>
          <div>
            <h2 class="text-sm font-semibold text-ink-gray-9">Bulk Edit Tasks</h2>
            <p class="text-[11px] text-ink-gray-5">
              Updating <span class="font-semibold text-ink-gray-9">{{ taskIds.length }}</span> selected tasks simultaneously
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="$emit('close')"
          class="p-1.5 text-ink-gray-4 hover:text-ink-gray-7 rounded-xl hover:bg-surface-gray-2 transition cursor-pointer"
        >
          <Icon name="x" size="16" />
        </button>
      </div>

      <!-- Body / Form Fields -->
      <div class="p-6 space-y-4 text-xs overflow-y-auto max-h-[70vh]">
        <div class="p-2.5 rounded-xl bg-surface-gray-1 border border-outline-gray-2 text-[11px] text-ink-gray-6 flex items-center justify-between">
          <span>Selected Tasks:</span>
          <span class="font-mono font-semibold text-ink-gray-9">{{ taskIds.length }} tasks</span>
        </div>

        <!-- 1. Status -->
        <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer font-medium text-ink-gray-8">
              <input
                type="checkbox"
                v-model="fieldsToUpdate.status"
                class="rounded border-outline-gray-3 text-ink-gray-9"
              />
              <span>Change Status</span>
            </label>
            <span v-if="fieldsToUpdate.status" class="text-[10px] text-emerald-600 font-medium">Will Update</span>
          </div>

          <select
            v-if="fieldsToUpdate.status"
            v-model="formData.status"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 focus:bg-white text-ink-gray-9 focus:outline-none transition cursor-pointer"
          >
            <option value="Open">Open</option>
            <option value="Working">Working</option>
            <option value="Pending Review">Pending Review</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>

        <!-- 2. Priority -->
        <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer font-medium text-ink-gray-8">
              <input
                type="checkbox"
                v-model="fieldsToUpdate.priority"
                class="rounded border-outline-gray-3 text-ink-gray-9"
              />
              <span>Change Priority</span>
            </label>
            <span v-if="fieldsToUpdate.priority" class="text-[10px] text-emerald-600 font-medium">Will Update</span>
          </div>

          <select
            v-if="fieldsToUpdate.priority"
            v-model="formData.priority"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 focus:bg-white text-ink-gray-9 focus:outline-none transition cursor-pointer"
          >
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Urgent">Urgent</option>
          </select>
        </div>

        <!-- 3. Assignee -->
        <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer font-medium text-ink-gray-8">
              <input
                type="checkbox"
                v-model="fieldsToUpdate.assigned_to"
                class="rounded border-outline-gray-3 text-ink-gray-9"
              />
              <span>Assign To Team Member</span>
            </label>
            <span v-if="fieldsToUpdate.assigned_to" class="text-[10px] text-emerald-600 font-medium">Will Update</span>
          </div>

          <input
            v-if="fieldsToUpdate.assigned_to"
            v-model="formData.assigned_to"
            type="email"
            placeholder="Enter user email (e.g. consultant@company.com)"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 focus:bg-white text-ink-gray-9 focus:outline-none transition"
          />
        </div>

        <!-- 4. Due Date -->
        <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer font-medium text-ink-gray-8">
              <input
                type="checkbox"
                v-model="fieldsToUpdate.exp_end_date"
                class="rounded border-outline-gray-3 text-ink-gray-9"
              />
              <span>Change Due Date</span>
            </label>
            <span v-if="fieldsToUpdate.exp_end_date" class="text-[10px] text-emerald-600 font-medium">Will Update</span>
          </div>

          <input
            v-if="fieldsToUpdate.exp_end_date"
            v-model="formData.exp_end_date"
            type="date"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 focus:bg-white text-ink-gray-9 focus:outline-none transition"
          />
        </div>

        <!-- 5. Module -->
        <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer font-medium text-ink-gray-8">
              <input
                type="checkbox"
                v-model="fieldsToUpdate.implementation_module"
                class="rounded border-outline-gray-3 text-ink-gray-9"
              />
              <span>Change Implementation Module</span>
            </label>
            <span v-if="fieldsToUpdate.implementation_module" class="text-[10px] text-emerald-600 font-medium">Will Update</span>
          </div>

          <select
            v-if="fieldsToUpdate.implementation_module"
            v-model="formData.implementation_module"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 focus:bg-white text-ink-gray-9 focus:outline-none transition cursor-pointer"
          >
            <option value="">Select Module...</option>
            <option v-for="m in modules" :key="m.name || m.module_code" :value="m.name || m.module_code">
              {{ m.module_name }}
            </option>
          </select>
        </div>

        <!-- 6. Key Milestone -->
        <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-white space-y-2">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer font-medium text-ink-gray-8">
              <input
                type="checkbox"
                v-model="fieldsToUpdate.is_milestone"
                class="rounded border-outline-gray-3 text-ink-gray-9"
              />
              <span>Set as Key Milestone</span>
            </label>
            <span v-if="fieldsToUpdate.is_milestone" class="text-[10px] text-emerald-600 font-medium">Will Update</span>
          </div>

          <div v-if="fieldsToUpdate.is_milestone" class="flex items-center gap-4 pt-1">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" :value="1" v-model="formData.is_milestone" />
              <span>Yes, Key Milestone</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" :value="0" v-model="formData.is_milestone" />
              <span>No, Standard Task</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-3.5 border-t border-outline-gray-2 bg-surface-gray-1 flex items-center justify-between rounded-b-2xl shrink-0">
        <button
          type="button"
          @click="$emit('close')"
          class="px-4 py-2 text-xs font-medium text-ink-gray-7 hover:text-ink-gray-9 rounded-xl hover:bg-surface-gray-2 transition cursor-pointer"
        >
          Cancel
        </button>

        <Button
          theme="gray"
          variant="solid"
          size="sm"
          :loading="submitting"
          :disabled="!hasAnyFieldSelected || submitting"
          label="Apply Changes"
          @click="handleApplyChanges"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button } from 'frappe-ui'
import Icon from './Icon.vue'
import { bulkUpdateTasks } from '../api'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  taskIds: {
    type: Array,
    default: () => [],
  },
  modules: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['close', 'updated'])

const submitting = ref(false)

const fieldsToUpdate = ref({
  status: false,
  priority: false,
  assigned_to: false,
  exp_end_date: false,
  implementation_module: false,
  is_milestone: false,
})

const formData = ref({
  status: 'Open',
  priority: 'Medium',
  assigned_to: '',
  exp_end_date: '',
  implementation_module: '',
  is_milestone: 0,
})

const hasAnyFieldSelected = computed(() => {
  return Object.values(fieldsToUpdate.value).some(Boolean)
})

async function handleApplyChanges() {
  if (!hasAnyFieldSelected.value || props.taskIds.length === 0) return

  const payload = {}
  if (fieldsToUpdate.value.status) payload.status = formData.value.status
  if (fieldsToUpdate.value.priority) payload.priority = formData.value.priority
  if (fieldsToUpdate.value.assigned_to) payload.assigned_to = formData.value.assigned_to
  if (fieldsToUpdate.value.exp_end_date) payload.exp_end_date = formData.value.exp_end_date
  if (fieldsToUpdate.value.implementation_module) payload.implementation_module = formData.value.implementation_module
  if (fieldsToUpdate.value.is_milestone) payload.is_milestone = formData.value.is_milestone

  submitting.value = true
  try {
    const res = await bulkUpdateTasks(props.taskIds, payload)
    if (res && res.success !== false) {
      emit('updated')
      emit('close')
    } else {
      alert(res?.message || 'Failed to bulk update tasks')
    }
  } catch (e) {
    alert('Error updating tasks: ' + (e.message || e))
  } finally {
    submitting.value = false
  }
}
</script>

