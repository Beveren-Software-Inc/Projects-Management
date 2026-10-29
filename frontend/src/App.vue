<template>
  <FrappeUIProvider>
    <div class="app-shell h-screen w-screen overflow-hidden antialiased select-none" :class="{ 'is-sidebar-collapsed': sidebarCollapsed }">
      <!-- Helpdesk-styled Sidebar -->
      <Sidebar
        :unread-count="unreadCount"
        :overdue-count="dashboardData.kpis?.overdue_tasks || 0"
        :is-search-open="showCommandPalette"
        :is-notifications-open="showNotifications"
        @toggle-collapsed="sidebarCollapsed = !sidebarCollapsed"
        @open-search="showCommandPalette = true"
        @open-notifications="showNotifications = !showNotifications"
        @open-new-project="showNewProjectModal = true"
        @open-new-task="openNewTaskModal(null)"
        @open-settings="showAppSettings = true"
      />

      <!-- Notifications Slide-Over Panel -->
      <NotificationPanel
        :is-open="showNotifications"
        :sidebar-width="220"
        @close="showNotifications = false"
        @count-changed="(count) => unreadCount = count"
      />

      <!-- Command Palette / Global Search Modal -->
      <CommandPalette
        :is-open="showCommandPalette"
        @close="showCommandPalette = false"
        @open="showCommandPalette = true"
        @open-new-project="showNewProjectModal = true"
        @open-new-task="openNewTaskModal(null)"
        @open-settings="showAppSettings = true"
      />

      <!-- Main View Content Area -->
      <main class="app-main">
        <router-view
          ref="pageRef"
          :data="dashboardData"
          @open-new-project="showNewProjectModal = true"
          @open-new-task="openNewTaskModal"
          @open-search="showCommandPalette = true"
          @open-notifications="showNotifications = !showNotifications"
          @refresh="refreshData"
        />
      </main>

      <!-- Modals -->
      <NewProjectModal
        :show="showNewProjectModal"
        @close="showNewProjectModal = false"
        @created="onProjectCreated"
      />

      <NewTaskModal
        :show="showNewTaskModal"
        :initial-project="selectedProjectForNewTask"
        @close="showNewTaskModal = false"
        @created="onTaskCreated"
      />

      <AppSettingsModal
        :show="showAppSettings"
        @close="showAppSettings = false"
      />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FrappeUIProvider } from 'frappe-ui'
import Sidebar from './components/Sidebar.vue'
import NewProjectModal from './components/NewProjectModal.vue'
import NewTaskModal from './components/NewTaskModal.vue'
import CommandPalette from './components/CommandPalette.vue'
import NotificationPanel from './components/NotificationPanel.vue'
import AppSettingsModal from './components/AppSettingsModal.vue'
import { getPortfolioDashboard, getNotifications } from './api'

const router = useRouter()
const pageRef = ref(null)

const showNewProjectModal = ref(false)
const showNewTaskModal = ref(false)
const showCommandPalette = ref(false)
const showNotifications = ref(false)
const showAppSettings = ref(false)
const sidebarCollapsed = ref(false)
const unreadCount = ref(0)
const selectedProjectForNewTask = ref('')
const dashboardData = ref({})

onMounted(async () => {
  await Promise.all([
    refreshData(),
    loadInitialNotifications(),
  ])
})

async function loadInitialNotifications() {
  try {
    const res = await getNotifications(10)
    unreadCount.value = res?.unread_count || 0
  } catch (e) {
    console.error('Failed to load initial notifications', e)
  }
}

async function refreshData() {
  try {
    dashboardData.value = await getPortfolioDashboard()
  } catch (e) {
    console.error('Failed to load portfolio stats', e)
  }
}

function openNewTaskModal(projectName = null) {
  selectedProjectForNewTask.value = projectName || ''
  showNewTaskModal.value = true
}

async function onProjectCreated(res) {
  await refreshData()
  if (res?.project_name) {
    router.push('/projects/' + res.project_name)
  }
}

async function onTaskCreated(task) {
  await refreshData()
  if (task?.project && task?.name) {
    await router.push({
      path: `/projects/${task.project}/tasks/${task.name}`,
      query: task.implementation_module ? { module: task.implementation_module } : {},
    })
  }
  pageRef.value?.loadProject?.()
}
</script>
