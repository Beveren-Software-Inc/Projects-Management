<template>
  <div
    class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-xs transition"
    :style="{
      backgroundColor: appColor || '#0f172a'
    }"
  >
    <!-- Custom attached icon if configured -->
    <Icon v-if="appIcon && appIcon !== 'diamond'" :name="appIcon" size="18" color="#ffffff" />

    <!-- Beveren teal diamond/wings icon default fallback -->
    <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L3 9L12 16L21 9L12 2Z" fill="#0D9488" />
      <path d="M12 16L3 9V15L12 22L21 15V9L12 16Z" fill="#14B8A6" />
    </svg>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Icon from './Icon.vue'

const appIcon = ref('')
const appColor = ref('')

onMounted(() => {
  loadLogo()
  window.addEventListener('storage', loadLogo)
})

function loadLogo() {
  try {
    const raw = localStorage.getItem('projects_app_settings')
    if (raw) {
      const parsed = JSON.parse(raw)
      appIcon.value = parsed.brandIcon || ''
      appColor.value = parsed.brandColor || ''
    }
  } catch (e) {}
}
</script>

