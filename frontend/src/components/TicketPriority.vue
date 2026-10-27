<template>
  <span
    v-if="priority"
    class="flex min-w-0 items-center gap-1.5"
    :class="{ 'me-1': iconOnly }"
  >
    <span class="flex h-3.5 w-3.5 shrink-0 items-center justify-center">
      <!-- Urgent -->
      <svg
        v-if="priority === 'Urgent'"
        class="h-3.5 w-3.5"
        viewBox="0 0 14 14"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="14" height="14" rx="4" class="fill-red-500" />
        <rect x="6.25" y="3" width="1.5" height="4.75" rx="0.75" class="fill-white" />
        <circle cx="7" cy="10" r="0.9" class="fill-white" />
      </svg>
      <!-- High / Medium / Low 3 bars -->
      <svg
        v-else
        class="h-3 w-3"
        viewBox="0 0 10 12"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect x="0" y="8" width="2.5" height="4" rx="0.5" :class="barClass(2)" />
        <rect x="4" y="4" width="2.5" height="8" rx="0.5" :class="barClass(1)" />
        <rect x="8" y="0" width="2.5" height="12" rx="0.5" :class="barClass(0)" />
      </svg>
    </span>
    <span v-if="!iconOnly" :title="priority" class="truncate font-medium text-xs text-ink-gray-8">
      {{ priority }}
    </span>
  </span>
</template>

<script setup>
const props = defineProps({
  priority: {
    type: String,
    default: 'Medium',
  },
  iconOnly: {
    type: Boolean,
    default: false,
  },
})

function barClass(barIdx) {
  // barIdx: 0 is highest, 1 is middle, 2 is lowest
  if (props.priority === 'High') {
    return 'fill-ink-gray-7'
  }
  if (props.priority === 'Medium') {
    return barIdx >= 1 ? 'fill-ink-gray-7' : 'fill-outline-gray-3'
  }
  // Low
  return barIdx === 2 ? 'fill-ink-gray-7' : 'fill-outline-gray-3'
}
</script>

