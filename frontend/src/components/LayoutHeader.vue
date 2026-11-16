<template>
  <header class="h-11 bg-surface-white border-b border-outline-gray-2 px-5 flex items-center justify-between shrink-0 select-none">
    <!-- Left Header (Breadcrumbs) -->
    <div class="flex items-center gap-1.5 min-w-0 flex-1">
      <slot name="left-header">
        <div class="flex items-center text-lg font-medium text-ink-gray-5 truncate">
          <router-link to="/tasks" class="hover:text-ink-gray-8 transition">Tasks</router-link>
          <span v-if="title" class="mx-1.5 text-ink-gray-4">/</span>
          <span v-if="title" class="text-ink-gray-9 font-semibold truncate">{{ title }}</span>
        </div>
      </slot>
    </div>

    <!-- Right Header (Actions & Status) -->
    <div class="flex items-center gap-2 shrink-0">
      <slot name="right-header" />
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '',
  },
})
</script>

