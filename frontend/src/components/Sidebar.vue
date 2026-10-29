<template>
  <aside class="app-sidebar" aria-label="Workspace">
    <div class="sidebar-brand">
      <div class="brand-mark brand-mark-logo" aria-hidden="true">
        <BrandLogo />
      </div>
      <div class="brand-copy">
        <span class="brand-name">{{ brandTitle }}</span>
        <span class="brand-user">{{ userName }}</span>
      </div>
    </div>

    <button class="sidebar-search" type="button" @click="$emit('open-search')">
      <Icon name="search" :size="15" />
      <span class="sidebar-search-label">Search</span>
      <kbd>⌘ K</kbd>
    </button>

    <nav class="sidebar-nav" aria-label="Workspace navigation">
      <div class="nav-section-label">WORKSPACE</div>
      <router-link class="sidebar-link" to="/dashboard" :class="{ active: route.path === '/dashboard' }">
        <Icon name="home" :size="16" />
        <span>Overview</span>
        <span v-if="route.path === '/dashboard'" class="active-indicator" />
      </router-link>
      <router-link class="sidebar-link" to="/tasks?assigned=me" :class="{ active: isAssigned }">
        <Icon name="list-todo" :size="16" />
        <span>My tasks</span>
      </router-link>
      <router-link class="sidebar-link" to="/projects" :class="{ active: route.path.startsWith('/projects') }">
        <Icon name="folder-kanban" :size="16" />
        <span>Projects</span>
        <span v-if="route.path.startsWith('/projects')" class="active-indicator" />
      </router-link>
      <router-link class="sidebar-link" to="/modules" :class="{ active: route.path.startsWith('/modules') }">
        <Icon name="layers" :size="16" />
        <span>Module templates</span>
      </router-link>

      <div class="nav-section-heading">
        <span>PUBLIC VIEWS</span>
        <button type="button" class="nav-section-toggle" @click="publicViewsOpen = !publicViewsOpen">
          <Icon name="chevron-down" :size="13" />
        </button>
      </div>
      <div v-if="publicViewsOpen" class="public-view-links">
        <router-link class="sidebar-link sidebar-link-sub" to="/tasks?assigned=me" :class="{ active: isAssigned }">
          <Icon name="users" :size="14" />
          <span>Assigned to me</span>
        </router-link>
        <router-link class="sidebar-link sidebar-link-sub" to="/tasks?filter=pending" :class="{ active: route.query.filter === 'pending' }">
          <Icon name="clock" :size="14" />
          <span>Pending tasks</span>
        </router-link>
        <router-link class="sidebar-link sidebar-link-sub" to="/tasks?filter=overdue" :class="{ active: route.query.filter === 'overdue' }">
          <Icon name="alert-circle" :size="14" />
          <span>Overdue tasks</span>
          <span v-if="overdueCount" class="nav-alert">{{ overdueCount }}</span>
        </router-link>
        <router-link class="sidebar-link sidebar-link-sub" to="/tasks?filter=milestones" :class="{ active: route.query.filter === 'milestones' }">
          <Icon name="flag" :size="14" />
          <span>Milestones</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-bottom">
      <a class="sidebar-link help-link" href="/app">
        <Icon name="help" :size="16" />
        <span>Help center</span>
      </a>
      <button class="profile-switcher" type="button" @click="menuOpen = !menuOpen">
        <span class="avatar avatar-small avatar-indigo">{{ initials(userName) }}</span>
        <span class="profile-copy">
          <strong>{{ userName }}</strong>
          <small>Workspace</small>
        </span>
        <Icon name="more-horizontal" :size="16" />
      </button>
      <div v-if="menuOpen" class="account-menu">
        <button type="button" @click="emit('open-settings'); menuOpen = false">App settings</button>
        <button type="button" @click="go('/app')">Switch to Desk</button>
        <button type="button" @click="go('/app/user')">My profile</button>
        <button type="button" @click="go('/api/method/logout')">Log out</button>
      </div>
      <button type="button" class="collapse-button" @click="$emit('toggle-collapsed')">
        <Icon name="panel-left" :size="15" />
        <span>Collapse</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import BrandLogo from './BrandLogo.vue'
import Icon from './Icon.vue'
import { sessionUserName } from '@/sessionUser'

defineProps({
  unreadCount: { type: Number, default: 0 },
  overdueCount: { type: Number, default: 0 },
  isSearchOpen: { type: Boolean, default: false },
  isNotificationsOpen: { type: Boolean, default: false },
})

const emit = defineEmits([
  'toggle-collapsed',
  'open-search',
  'open-notifications',
  'open-new-project',
  'open-new-task',
  'open-settings',
])

const route = useRoute()
const publicViewsOpen = ref(true)
const menuOpen = ref(false)
const userName = computed(() => sessionUserName())
const brandTitle = computed(() => {
  try {
    const raw = localStorage.getItem('projects_app_settings')
    const name = raw ? JSON.parse(raw).brandName : ''
    if (name) return name
  } catch (e) {}
  return 'Beveren'
})
const isAssigned = computed(() => route.path === '/tasks' && route.query.assigned === 'me')

function initials(name) {
  const parts = String(name || '?').trim().split(/\s+/).slice(0, 2)
  return parts.map(part => part[0]?.toUpperCase() || '').join('') || '?'
}

function go(url) {
  menuOpen.value = false
  window.location.href = url
}
</script>
