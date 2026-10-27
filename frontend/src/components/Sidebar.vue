<template>
  <Sidebar v-model:collapsed="collapsed" class="select-none border-r border-outline-gray-2 bg-[#f8f9fa] helpdesk-sidebar">
    <!-- 1. Header: Beveren Software + Abid Khan with Beveren Logo -->
    <SidebarHeader
      title="Beveren Software"
      subtitle="Abid Khan"
      :menu-items="workspaceMenu"
    >
      <template #prefix>
        <BrandLogo />
      </template>
    </SidebarHeader>

    <!-- 2. Scrollable Navigation List -->
    <div class="flex-1 overflow-y-auto space-y-0.5 px-0.5">
      <!-- Search & Notifications Quick items -->
      <SidebarItem
        label="Search"
        icon="lucide-search"
        :active="isSearchOpen"
        @click="$emit('open-search')"
      >
        <template #suffix>
          <kbd v-if="!collapsed" class="px-1.5 py-0.2 text-[10px] rounded bg-surface-gray-2 text-ink-gray-5 font-mono">^ K</kbd>
        </template>
      </SidebarItem>

      <SidebarItem
        label="Notifications"
        icon="lucide-bell"
        :active="isNotificationsOpen"
        @click="$emit('open-notifications')"
      >
        <template #suffix>
          <Badge v-if="!collapsed && unreadCount > 0" theme="blue" variant="subtle" size="sm" :label="unreadCount" />
        </template>
      </SidebarItem>

      <!-- Main Menu Items matching Frappe Helpdesk -->
      <SidebarItem
        label="Home"
        icon="lucide-home"
        route="/dashboard"
        :active="route.path === '/dashboard' && route.query.tab !== 'metrics'"
      />
      <SidebarItem
        label="Dashboard"
        icon="lucide-layout-dashboard"
        route="/dashboard?tab=metrics"
        :active="route.query.tab === 'metrics'"
      />
      <SidebarItem
        label="Projects"
        icon="lucide-folder-kanban"
        route="/projects"
        :active="route.path.startsWith('/projects')"
      />
      <SidebarItem
        label="Tasks"
        icon="lucide-ticket"
        route="/tasks"
        :active="isMainTasksActive()"
      />
      <SidebarItem
        label="Module Templates"
        icon="lucide-layers"
        route="/modules"
        :active="route.path.startsWith('/modules')"
      />

      <!-- Public Views (Collapsible Section matching Helpdesk) -->
      <SidebarSection label="Public Views" collapsible>
        <SidebarItem
          label="My Assigned Tasks"
          icon="lucide-user"
          route="/tasks?assigned=me"
          :active="route.path === '/tasks' && route.query.assigned === 'me'"
        />
        <SidebarItem
          label="Pending Tasks"
          icon="lucide-clock"
          route="/tasks?filter=pending"
          :active="route.path === '/tasks' && route.query.filter === 'pending'"
        />
        <SidebarItem
          label="Overdue Tasks"
          icon="lucide-alert-circle"
          route="/tasks?filter=overdue"
          :active="route.path === '/tasks' && route.query.filter === 'overdue'"
        />
        <SidebarItem
          label="Milestones"
          icon="lucide-flag"
          route="/tasks?filter=milestones"
          :active="route.path === '/tasks' && route.query.filter === 'milestones'"
        />
      </SidebarSection>
    </div>

    <!-- 3. Bottom Collapse Toggle -->
    <SidebarCollapseToggle class="mt-auto" />
  </Sidebar>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  Sidebar,
  SidebarHeader,
  SidebarItem,
  SidebarLabel,
  SidebarSection,
  SidebarCollapseToggle,
  Badge,
} from 'frappe-ui'
import BrandLogo from './BrandLogo.vue'
import Icon from './Icon.vue'

defineProps({
  unreadCount: {
    type: Number,
    default: 0,
  },
  isSearchOpen: {
    type: Boolean,
    default: false,
  },
  isNotificationsOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'open-search',
  'open-notifications',
  'open-new-project',
  'open-new-task',
  'open-settings',
])

const route = useRoute()
const collapsed = ref(false)

const workspaceMenu = [
  { label: 'App Settings', icon: 'lucide-settings', onClick: () => emit('open-settings') },
  { label: 'Switch to Frappe Desk', icon: 'lucide-external-link', onClick: () => window.location.href = '/app' },
  { label: 'My Profile', icon: 'lucide-user', onClick: () => window.location.href = '/app/user' },
  { label: 'Log out', icon: 'lucide-log-out', onClick: () => window.location.href = '/api/method/logout' },
]

function isMainTasksActive() {
  if (route.path !== '/tasks') return false
  if (route.query.filter || route.query.assigned) return false
  return true
}

function openHelp() {
  window.open('https://docs.frappe.io/erpnext', '_blank')
}
</script>
