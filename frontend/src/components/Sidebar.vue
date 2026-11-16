<template>
  <Sidebar
    v-model:collapsed="isCollapsed"
    class="select-none border-r border-outline-gray-2 bg-surface-white"
  >
    <!-- 1. Header: Company name + logged-in user with brand logo -->
    <SidebarHeader
      :title="companyName"
      :subtitle="currentUserName"
      :menu-items="workspaceMenu"
    >
      <template #prefix>
        <BrandLogo />
      </template>
    </SidebarHeader>

    <!-- 2. Scrollable Navigation List -->
    <div class="flex-1 overflow-y-auto px-1 space-y-0.5">
      <!-- Search & Notifications Quick items -->
      <SidebarItem
        label="Search"
        icon="lucide-search"
        :active="isSearchOpen"
        @click="$emit('open-search')"
      >
        <template #suffix>
          <kbd v-if="!isCollapsed" class="px-1.5 py-0.5 text-xs rounded bg-surface-gray-2 text-ink-gray-5 font-mono">⌘K</kbd>
        </template>
      </SidebarItem>

      <SidebarItem
        label="Notifications"
        icon="lucide-bell"
        :active="isNotificationsOpen"
        @click="$emit('open-notifications')"
      >
        <template #suffix>
          <Badge
            v-if="!isCollapsed && unreadCount > 0"
            theme="blue"
            variant="subtle"
            size="sm"
            :label="unreadCount"
          />
        </template>
      </SidebarItem>

      <!-- Main Navigation Items -->
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
        icon="lucide-check-square"
        route="/tasks"
        :active="isMainTasksActive()"
      />
      <SidebarItem
        label="Module Templates"
        icon="lucide-layers"
        route="/modules"
        :active="route.path.startsWith('/modules')"
      />

      <!-- Public Views (Collapsible Section) -->
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
import { useRoute } from 'vue-router'
import {
  Sidebar,
  SidebarHeader,
  SidebarItem,
  SidebarSection,
  SidebarCollapseToggle,
  Badge,
} from 'frappe-ui'
import BrandLogo from './BrandLogo.vue'

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

const isCollapsed = defineModel('collapsed', { default: false })

const emit = defineEmits([
  'open-search',
  'open-notifications',
  'open-new-project',
  'open-new-task',
  'open-settings',
])

const route = useRoute()

// Brand = company name and subtitle = logged-in user, both from the page boot (projects/www/projects.py)
const companyName = window.company_name || 'Projects'
const currentUserName =
  window.user_info?.full_name ||
  window.user_info?.email ||
  window.session_user ||
  ''

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
</script>
