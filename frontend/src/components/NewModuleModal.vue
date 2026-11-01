<template>
  <Dialog
    :model-value="show"
    @update:model-value="$emit('close')"
    :title="isEditing ? 'Edit Module Details' : 'Add New Module / Custom Module'"
    size="lg"
  >
    <template #title>
      <div class="flex items-center gap-3">
        <div
          class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border transition"
          :style="{
            backgroundColor: form.color + '18',
            borderColor: form.color + '40',
            color: form.color
          }"
        >
          <Icon :name="form.icon || 'Package'" size="18" :color="form.color" />
        </div>
        <div>
          <h2 class="text-sm font-semibold text-ink-gray-9">
            {{ isEditing ? 'Edit Module Details' : 'Add New Module / Custom Module' }}
          </h2>
          <p class="text-[11px] text-ink-gray-5">
            {{ isEditing ? 'Update module name, icon, color, and description.' : 'Create a custom ERPNext implementation module with standard task templates.' }}
          </p>
        </div>
      </div>
    </template>

    <form @submit.prevent="handleSubmit" class="space-y-4 pt-1 max-h-[65vh] overflow-y-auto px-1">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <TextInput
          v-model="form.module_name"
          label="Module Name *"
          placeholder="e.g. Quality Assurance & Inspection"
          size="sm"
          required
          @input="onNameInput"
        />

        <TextInput
          v-model="form.module_code"
          label="Module Code *"
          placeholder="e.g. quality_assurance"
          :disabled="isEditing"
          size="sm"
          required
        />
      </div>

      <div class="space-y-1">
        <label class="block text-xs font-medium text-ink-gray-7">Description</label>
        <Textarea
          v-model="form.description"
          rows="2"
          placeholder="Briefly describe implementation tasks and configurations included..."
          size="sm"
        />
      </div>

      <!-- Color Palette Selection -->
      <div>
        <label class="block text-xs font-medium text-ink-gray-7 mb-1.5">
          Module Theme Color
        </label>
        <div class="flex flex-wrap items-center gap-2">
          <button
            v-for="c in COLOR_OPTIONS"
            :key="c"
            type="button"
            @click="form.color = c"
            class="w-6 h-6 rounded-full transition-all flex items-center justify-center cursor-pointer border"
            :style="{
              backgroundColor: c,
              borderColor: form.color === c ? '#1E293B' : 'transparent',
              transform: form.color === c ? 'scale(1.15)' : 'scale(1)'
            }"
            :title="c"
          >
            <span v-if="form.color === c" class="text-white text-[10px] font-bold">✓</span>
          </button>
        </div>
      </div>

      <!-- Icon Selection -->
      <div>
        <label class="block text-xs font-medium text-ink-gray-7 mb-1.5">
          Module Icon
        </label>
        <div class="grid grid-cols-10 gap-1.5 p-2 bg-surface-gray-1 rounded-xl border border-outline-gray-2 max-h-36 overflow-y-auto">
          <button
            v-for="iconItem in ICON_OPTIONS"
            :key="iconItem"
            type="button"
            @click="form.icon = iconItem"
            class="p-2 rounded-lg flex items-center justify-center transition cursor-pointer"
            :class="form.icon === iconItem
              ? 'bg-white shadow-2xs border border-outline-gray-3 text-ink-gray-9 scale-105'
              : 'text-ink-gray-5 hover:text-ink-gray-8 hover:bg-surface-gray-2'"
            :title="iconItem"
          >
            <Icon :name="iconItem" size="16" />
          </button>
        </div>
      </div>

      <!-- Initial Task (Only for new modules) -->
      <div v-if="!isEditing" class="p-3 bg-surface-gray-1 rounded-xl border border-outline-gray-2 space-y-2">
        <Checkbox
          v-model="addInitialTask"
          label="Include initial setup task template"
        />
        <div v-if="addInitialTask" class="pt-1">
          <TextInput
            v-model="initialTaskSubject"
            placeholder="e.g. Quality Inspection Setup & Review"
            size="sm"
          />
        </div>
      </div>
    </form>

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
          :loading="loading"
          :label="isEditing ? 'Save Changes' : 'Create Module'"
          @click="handleSubmit"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Dialog,
  Button,
  TextInput,
  Textarea,
  Checkbox,
  toast,
} from 'frappe-ui'
import Icon from './Icon.vue'
import { createImplementationModule, saveModuleTemplate } from '../api'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  moduleData: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEditing = computed(() => Boolean(props.moduleData?.module_code))

const COLOR_OPTIONS = [
  '#10B981', // Emerald
  '#3B82F6', // Blue
  '#6366F1', // Indigo
  '#8B5CF6', // Violet
  '#EC4899', // Pink
  '#F59E0B', // Amber
  '#F97316', // Orange
  '#06B6D4', // Cyan
  '#14B8A6', // Teal
  '#F43F5E', // Rose
  '#A855F7', // Purple
  '#64748B', // Slate
]

const ICON_OPTIONS = [
  'Package',
  'Cpu',
  'CreditCard',
  'ShoppingCart',
  'TrendingUp',
  'Users',
  'Target',
  'LifeBuoy',
  'Server',
  'Shield',
  'Wrench',
  'Truck',
  'Zap',
  'Award',
  'FileText',
  'Database',
  'Briefcase',
  'Settings',
  'layers',
  'check-square',
]

const form = ref({
  module_name: '',
  module_code: '',
  description: '',
  color: '#3B82F6',
  icon: 'Package',
})

const addInitialTask = ref(true)
const initialTaskSubject = ref('')

watch(
  () => props.show,
  (val) => {
    if (val) {
      if (props.moduleData) {
        form.value = {
          module_name: props.moduleData.module_name || '',
          module_code: props.moduleData.module_code || '',
          description: props.moduleData.description || '',
          color: props.moduleData.color || '#3B82F6',
          icon: props.moduleData.icon || 'Package',
        }
      } else {
        form.value = {
          module_name: '',
          module_code: '',
          description: '',
          color: '#3B82F6',
          icon: 'Package',
        }
        addInitialTask.value = true
        initialTaskSubject.value = ''
      }
    }
  },
  { immediate: true }
)

function onNameInput() {
  if (!isEditing.value) {
    const raw = form.value.module_name || ''
    form.value.module_code = raw
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '')
    
    if (addInitialTask.value && !initialTaskSubject.value) {
      initialTaskSubject.value = `${form.value.module_name} Architecture & Setup`
    }
  }
}

async function handleSubmit() {
  if (!form.value.module_name.trim()) {
    toast.error('Please enter a module name')
    return
  }
  loading.value = true

  try {
    if (isEditing.value) {
      await saveModuleTemplate(form.value.module_code, {
        module_name: form.value.module_name,
        description: form.value.description,
        color: form.value.color,
        icon: form.value.icon,
      })
      toast.success('Module updated successfully')
      emit('saved', form.value.module_code)
      emit('close')
    } else {
      const tasks = []
      if (addInitialTask.value && initialTaskSubject.value.trim()) {
        tasks.push({
          subject: initialTaskSubject.value.trim(),
          description: `Initial configuration and workflow architecture for ${form.value.module_name}.`,
          day_offset: 1,
          duration_days: 3,
          expected_hours: 8,
          priority: 'High',
          is_milestone: 0,
        })
      }

      await createImplementationModule({
        module_name: form.value.module_name,
        module_code: form.value.module_code,
        description: form.value.description,
        color: form.value.color,
        icon: form.value.icon,
        tasks: JSON.stringify(tasks),
      })

      toast.success('Module created successfully')
      emit('saved', form.value.module_code)
      emit('close')
    }
  } catch (e) {
    toast.error('Failed to save module: ' + (e.message || e))
  } finally {
    loading.value = false
  }
}
</script>
