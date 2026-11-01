<template>
  <Dialog
    :model-value="show"
    @update:model-value="$emit('close')"
    title="Bulk Edit Tasks"
    size="lg"
  >
    <div class="space-y-4 pt-1 max-h-[65vh] overflow-y-auto px-1">
      <div class="p-2.5 rounded-xl bg-surface-gray-1 border border-outline-gray-2 text-[11px] text-ink-gray-6 flex items-center justify-between">
        <span>Selected Tasks:</span>
        <Badge theme="gray" variant="subtle" size="sm" :label="taskIds.length + ' tasks'" />
      </div>

      <!-- 1. Status -->
      <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-surface-white space-y-2">
        <div class="flex items-center justify-between">
          <Checkbox
            v-model="fieldsToUpdate.status"
            label="Change Status"
          />
          <Badge v-if="fieldsToUpdate.status" theme="green" variant="subtle" size="sm" label="Will Update" />
        </div>

        <Select
          v-if="fieldsToUpdate.status"
          v-model="formData.status"
          :options="[
            { label: 'Open', value: 'Open' },
            { label: 'Working', value: 'Working' },
            { label: 'Pending Review', value: 'Pending Review' },
            { label: 'Completed', value: 'Completed' },
            { label: 'Cancelled', value: 'Cancelled' },
          ]"
          size="sm"
        />
      </div>

      <!-- 2. Priority -->
      <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-surface-white space-y-2">
        <div class="flex items-center justify-between">
          <Checkbox
            v-model="fieldsToUpdate.priority"
            label="Change Priority"
          />
          <Badge v-if="fieldsToUpdate.priority" theme="green" variant="subtle" size="sm" label="Will Update" />
        </div>

        <Select
          v-if="fieldsToUpdate.priority"
          v-model="formData.priority"
          :options="[
            { label: 'Low', value: 'Low' },
            { label: 'Medium', value: 'Medium' },
            { label: 'High', value: 'High' },
            { label: 'Urgent', value: 'Urgent' },
          ]"
          size="sm"
        />
      </div>

      <!-- 3. Assignee -->
      <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-surface-white space-y-2">
        <div class="flex items-center justify-between">
          <Checkbox
            v-model="fieldsToUpdate.assigned_to"
            label="Assign To Team Member"
          />
          <Badge v-if="fieldsToUpdate.assigned_to" theme="green" variant="subtle" size="sm" label="Will Update" />
        </div>

        <TextInput
          v-if="fieldsToUpdate.assigned_to"
          v-model="formData.assigned_to"
          type="email"
          placeholder="consultant@beverensoftware.com"
          size="sm"
        />
      </div>

      <!-- 4. Due Date -->
      <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-surface-white space-y-2">
        <div class="flex items-center justify-between">
          <Checkbox
            v-model="fieldsToUpdate.exp_end_date"
            label="Change Due Date"
          />
          <Badge v-if="fieldsToUpdate.exp_end_date" theme="green" variant="subtle" size="sm" label="Will Update" />
        </div>

        <TextInput
          v-if="fieldsToUpdate.exp_end_date"
          v-model="formData.exp_end_date"
          type="date"
          size="sm"
        />
      </div>

      <!-- 5. Module -->
      <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-surface-white space-y-2">
        <div class="flex items-center justify-between">
          <Checkbox
            v-model="fieldsToUpdate.implementation_module"
            label="Change Implementation Module"
          />
          <Badge v-if="fieldsToUpdate.implementation_module" theme="green" variant="subtle" size="sm" label="Will Update" />
        </div>

        <Select
          v-if="fieldsToUpdate.implementation_module"
          v-model="formData.implementation_module"
          placeholder="Select Module..."
          :options="moduleOptions"
          size="sm"
        />
      </div>

      <!-- 6. Key Milestone -->
      <div class="p-3.5 rounded-xl border border-outline-gray-2 bg-surface-white space-y-2">
        <div class="flex items-center justify-between">
          <Checkbox
            v-model="fieldsToUpdate.is_milestone"
            label="Set as Key Milestone"
          />
          <Badge v-if="fieldsToUpdate.is_milestone" theme="green" variant="subtle" size="sm" label="Will Update" />
        </div>

        <div v-if="fieldsToUpdate.is_milestone" class="flex items-center gap-4 pt-1">
          <label class="flex items-center gap-2 cursor-pointer text-xs">
            <input type="radio" :value="1" v-model="formData.is_milestone" />
            <span>Yes, Key Milestone</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer text-xs">
            <input type="radio" :value="0" v-model="formData.is_milestone" />
            <span>No, Standard Task</span>
          </label>
        </div>
      </div>
    </div>

    <template #actions>
      <div class="flex items-center justify-end gap-2 w-full">
        <Button
          variant="subtle"
          size="sm"
          label="Cancel"
          @click="$emit('close')"
        />
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
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Dialog,
  Button,
  Badge,
  Checkbox,
  Select,
  TextInput,
  toast,
} from 'frappe-ui'
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

const moduleOptions = computed(() => {
  return [
    { label: '-- Select Module --', value: '' },
    ...props.modules.map(m => ({
      label: m.module_name,
      value: m.name || m.module_code,
    })),
  ]
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
      toast.success(`Successfully updated ${props.taskIds.length} tasks`)
      emit('updated')
      emit('close')
    } else {
      toast.error(res?.message || 'Failed to bulk update tasks')
    }
  } catch (e) {
    toast.error('Error updating tasks: ' + (e.message || e))
  } finally {
    submitting.value = false
  }
}
</script>
