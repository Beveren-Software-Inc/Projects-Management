<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 select-none"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl border border-outline-gray-2 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150"
      @click.stop
    >
      <!-- Header -->
      <div class="px-5 py-4 border-b border-outline-gray-2 flex items-center justify-between bg-white rounded-t-2xl">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border transition"
            :style="{
              backgroundColor: form.color + '18',
              borderColor: form.color + '40',
              color: form.color
            }"
          >
            <Icon :name="form.icon || 'Package'" size="20" :color="form.color" />
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

        <button
          type="button"
          @click="$emit('close')"
          class="p-1.5 text-ink-gray-4 hover:text-ink-gray-7 rounded-xl hover:bg-surface-gray-2 transition cursor-pointer"
        >
          <Icon name="x" size="16" />
        </button>
      </div>

      <!-- Form Body -->
      <form @submit.prevent="handleSubmit" class="p-5 space-y-4 bg-white text-xs">
        <!-- Module Name & Code -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">
              Module Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.module_name"
              type="text"
              placeholder="e.g. Quality Assurance & Inspection"
              class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
              required
              @input="onNameInput"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">
              Module Code <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.module_code"
              type="text"
              placeholder="e.g. quality_assurance"
              :disabled="isEditing"
              class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs disabled:opacity-60 disabled:cursor-not-allowed font-mono"
              required
            />
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">
            Description
          </label>
          <textarea
            v-model="form.description"
            rows="2"
            placeholder="Briefly describe what implementation tasks and configurations this module includes..."
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs resize-none"
          ></textarea>
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
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="addInitialTask"
              type="checkbox"
              class="rounded-md border-outline-gray-3 text-ink-gray-9 focus:ring-0"
            />
            <span class="text-xs font-medium text-ink-gray-8">Include initial setup task template</span>
          </label>
          <div v-if="addInitialTask" class="pt-1">
            <input
              v-model="initialTaskSubject"
              type="text"
              placeholder="e.g. Quality Inspection Setup & Review"
              class="w-full px-2.5 py-1 text-xs rounded-xl border border-outline-gray-2 bg-white text-ink-gray-9 focus:outline-none focus:border-outline-gray-4"
            />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="pt-2 flex items-center justify-end gap-2 border-t border-outline-gray-1">
          <Button
            type="button"
            variant="subtle"
            size="sm"
            label="Cancel"
            @click="$emit('close')"
          />
          <Button
            type="submit"
            variant="solid"
            size="sm"
            :loading="loading"
            :label="isEditing ? 'Save Changes' : 'Create Module'"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button } from 'frappe-ui'
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
  if (!form.value.module_name.trim()) return
  loading.value = true

  try {
    if (isEditing.value) {
      await saveModuleTemplate(form.value.module_code, {
        module_name: form.value.module_name,
        description: form.value.description,
        color: form.value.color,
        icon: form.value.icon,
      })
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

      emit('saved', form.value.module_code)
      emit('close')
    }
  } catch (e) {
    alert('Failed to save module: ' + (e.message || e))
  } finally {
    loading.value = false
  }
}
</script>

