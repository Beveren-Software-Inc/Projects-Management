<template>
  <header class="h-14 bg-surface-white border-b border-outline-gray-2 px-6 flex items-center justify-between shrink-0 select-none">
    <!-- Left: Page Title / Breadcrumbs -->
    <div class="flex items-center gap-3">
      <h1 class="text-base font-semibold text-ink-gray-9">{{ title }}</h1>
      <span v-if="subtitle" class="text-sm text-ink-gray-5 bg-surface-gray-2 px-2 py-0.5 rounded-full border border-outline-gray-2">
        {{ subtitle }}
      </span>
    </div>

    <!-- Right: Search & Actions -->
    <div class="flex items-center gap-3">
      <!-- Search Input -->
      <div class="relative w-64">
        <Icon name="search" size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-gray-4" />
        <input
          type="text"
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
          placeholder="Search projects, tasks, clients..."
          class="w-full pl-9 pr-3 py-1.5 text-sm rounded-xl bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white border border-outline-gray-2 focus:border-outline-gray-4 text-ink-gray-8 placeholder-ink-gray-4 focus:outline-none transition shadow-2xs"
        />
      </div>

      <!-- Action buttons -->
      <button
        @click="$emit('refresh')"
        title="Refresh data"
        class="p-2 text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-gray-2 rounded-xl border border-outline-gray-2 transition"
      >
        <Icon name="refresh" size="14" />
      </button>

      <button
        @click="$emit('open-new-task')"
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-xl border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-2 transition shadow-2xs"
      >
        <Icon name="plus" size="13" />
        <span>New Task</span>
      </button>

      <button
        @click="$emit('open-new-project')"
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-xl bg-ink-gray-9 text-white hover:bg-black shadow-sm transition"
      >
        <Icon name="plus" size="13" />
        <span>New Project</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  title: {
    type: String,
    default: 'Dashboard',
  },
  subtitle: {
    type: String,
    default: '',
  },
  modelValue: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue', 'refresh', 'open-new-project', 'open-new-task'])
</script>

