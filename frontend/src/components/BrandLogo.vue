<template>
  <img
    :src="src"
    alt="Beveren"
    class="h-full w-full object-contain"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'light',
  },
})

const src = computed(() =>
  props.variant === 'dark'
    ? '/assets/projects/brand/icon-dark.jpg'
    : '/assets/projects/brand/icon-light.jpg'
)
</script>
