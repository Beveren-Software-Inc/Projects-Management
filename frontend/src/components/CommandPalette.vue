<template>
  <div
    v-if="isOpen"
    class="palette-overlay fixed inset-0 z-[100] flex justify-center items-start pt-[10vh] p-4 bg-black/50 backdrop-blur-sm select-none"
    @click.self="close"
    @keydown.escape="close"
  >
    <div
      class="palette-content w-full max-w-[640px] !bg-white rounded-2xl shadow-2xl border border-outline-gray-3 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150"
      @keydown.down.prevent="navigateResults(1)"
      @keydown.up.prevent="navigateResults(-1)"
      @keydown.enter.prevent="selectActiveItem"
    >
      <!-- Search Input Header -->
      <div class="p-3 border-b border-outline-gray-1 !bg-white rounded-t-2xl">
        <div class="flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-surface-gray-1/70 border border-outline-gray-2 focus-within:border-outline-gray-4 focus-within:bg-white transition shadow-2xs">
          <Icon name="search" size="16" class="text-ink-gray-5 shrink-0" />
          <input
            ref="inputRef"
            v-model="query"
            type="text"
            placeholder="Search tasks, projects, modules, or actions..."
            class="flex-1 text-sm bg-transparent border-none text-ink-gray-9 placeholder:text-ink-gray-4 focus:outline-none"
            autocomplete="off"
          />
          <div class="flex items-center gap-1.5 shrink-0">
            <kbd class="px-2 py-0.5 text-[10px] rounded-md bg-surface-gray-2 text-ink-gray-5 font-mono border border-outline-gray-2 shadow-2xs">
              ESC
            </kbd>
          </div>
        </div>
      </div>

      <!-- Search Results / Commands Body -->
      <div class="max-h-[380px] overflow-y-auto p-2 space-y-4 !bg-white">
        <!-- 1. Searching Spinner -->
        <div v-if="searching" class="py-8 text-center text-xs text-ink-gray-4 flex items-center justify-center gap-2">
          <Icon name="refresh" size="14" class="animate-spin text-ink-gray-6" />
          <span>Searching...</span>
        </div>

        <!-- 2. No Results State -->
        <div v-else-if="query && flattenedItems.length === 0" class="py-12 text-center text-xs text-ink-gray-4">
          No matches found for "<span class="font-medium text-ink-gray-7">{{ query }}</span>"
        </div>

        <!-- 3. Categorized Items -->
        <template v-else>
          <!-- Tasks Category -->
          <div v-if="results.tasks?.length > 0">
            <div class="px-3 py-1 text-[11px] font-semibold text-ink-gray-4 uppercase tracking-wider">
              Tasks
            </div>
            <div class="space-y-0.5 mt-1">
              <div
                v-for="item in results.tasks"
                :key="item.name"
                @click="handleSelect(item)"
                @mouseenter="setActive(item)"
                class="px-3 py-2 rounded-xl text-xs flex items-center justify-between cursor-pointer transition"
                :class="activeItem?.id === item.id ? 'bg-surface-gray-2 text-ink-gray-9 font-medium' : 'text-ink-gray-7 hover:bg-surface-gray-1'"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <div class="w-6 h-6 rounded-lg bg-surface-gray-2 flex items-center justify-center shrink-0">
                    <Icon name="ticket" size="13" class="text-ink-gray-6" />
                  </div>
                  <span class="font-mono text-[11px] text-ink-gray-4 shrink-0">#{{ item.name.split('-').pop() }}</span>
                  <span class="truncate">{{ item.subject }}</span>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <Badge theme="gray" variant="subtle" size="sm" :label="item.status" />
                </div>
              </div>
            </div>
          </div>

          <!-- Projects Category -->
          <div v-if="results.projects?.length > 0">
            <div class="px-3 py-1 text-[11px] font-semibold text-ink-gray-4 uppercase tracking-wider">
              Projects
            </div>
            <div class="space-y-0.5 mt-1">
              <div
                v-for="item in results.projects"
                :key="item.name"
                @click="handleSelect(item)"
                @mouseenter="setActive(item)"
                class="px-3 py-2 rounded-xl text-xs flex items-center justify-between cursor-pointer transition"
                :class="activeItem?.id === item.id ? 'bg-surface-gray-2 text-ink-gray-9 font-medium' : 'text-ink-gray-7 hover:bg-surface-gray-1'"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <div class="w-6 h-6 rounded-lg bg-surface-gray-2 flex items-center justify-center shrink-0">
                    <Icon name="folder-kanban" size="13" class="text-ink-gray-6" />
                  </div>
                  <span class="truncate">{{ item.project_name }}</span>
                </div>
                <div class="flex items-center gap-2 shrink-0 text-[11px] text-ink-gray-5">
                  <span>{{ item.percent_complete || 0 }}% done</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Navigation / Actions -->
          <div v-if="filteredActions.length > 0">
            <div class="px-3 py-1 text-[11px] font-semibold text-ink-gray-4 uppercase tracking-wider">
              Actions & Navigation
            </div>
            <div class="space-y-0.5 mt-1">
              <div
                v-for="action in filteredActions"
                :key="action.id"
                @click="handleSelect(action)"
                @mouseenter="setActive(action)"
                class="px-3 py-2 rounded-xl text-xs flex items-center justify-between cursor-pointer transition"
                :class="activeItem?.id === action.id ? 'bg-surface-gray-2 text-ink-gray-9 font-medium' : 'text-ink-gray-7 hover:bg-surface-gray-1'"
              >
                <div class="flex items-center gap-2.5">
                  <div class="w-6 h-6 rounded-lg bg-surface-gray-2 flex items-center justify-center shrink-0">
                    <Icon :name="action.icon" size="13" class="text-ink-gray-6" />
                  </div>
                  <span>{{ action.label }}</span>
                </div>
                <span class="text-[11px] text-ink-gray-4 font-mono">{{ action.shortcut || '↵' }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Footer Toolbar -->
      <div class="px-4 py-2.5 bg-surface-gray-1 border-t border-outline-gray-1 flex items-center justify-between text-[11px] text-ink-gray-5 rounded-b-2xl">
        <div class="flex items-center gap-3">
          <span class="flex items-center gap-1">
            <kbd class="px-1.5 py-0.5 rounded-md bg-white border border-outline-gray-2 font-mono shadow-2xs">↑</kbd>
            <kbd class="px-1.5 py-0.5 rounded-md bg-white border border-outline-gray-2 font-mono shadow-2xs">↓</kbd>
            to navigate
          </span>
          <span class="flex items-center gap-1">
            <kbd class="px-1.5 py-0.5 rounded-md bg-white border border-outline-gray-2 font-mono shadow-2xs">↵</kbd>
            to select
          </span>
        </div>
        <div>
          <span>Frappe Helpdesk Command Palette</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Badge } from 'frappe-ui'
import Icon from './Icon.vue'
import { globalSearch } from '../api'

const props = defineProps({
  isOpen: Boolean,
})

const emit = defineEmits(['close', 'open-new-project', 'open-new-task', 'open-settings'])

const router = useRouter()
const inputRef = ref(null)
const query = ref('')
const searching = ref(false)
const results = ref({ tasks: [], projects: [], modules: [] })
const activeIndex = ref(0)

const defaultActions = [
  { id: 'act-new-task', type: 'action', label: 'Create New Task', icon: 'plus', action: 'open-new-task' },
  { id: 'act-new-project', type: 'action', label: 'Create Implementation Project', icon: 'plus', action: 'open-new-project' },
  { id: 'act-settings', type: 'action', label: 'App Settings & Branding', icon: 'settings', action: 'open-settings' },
  { id: 'nav-dashboard', type: 'nav', label: 'Go to Home', icon: 'home', route: '/dashboard' },
  { id: 'nav-projects', type: 'nav', label: 'Go to Projects', icon: 'folder-kanban', route: '/projects' },
  { id: 'nav-tasks', type: 'nav', label: 'Go to Tasks', icon: 'ticket', route: '/tasks' },
  { id: 'nav-modules', type: 'nav', label: 'Go to Module Templates', icon: 'layers', route: '/modules' },
]

const filteredActions = computed(() => {
  if (!query.value.trim()) return defaultActions
  const q = query.value.toLowerCase()
  return defaultActions.filter(a => a.label.toLowerCase().includes(q))
})

const flattenedItems = computed(() => {
  const items = []
  if (results.value.tasks) {
    results.value.tasks.forEach(t => items.push({ ...t, id: 'task-' + t.name, itemType: 'task' }))
  }
  if (results.value.projects) {
    results.value.projects.forEach(p => items.push({ ...p, id: 'proj-' + p.name, itemType: 'project' }))
  }
  filteredActions.value.forEach(a => items.push({ ...a, itemType: a.type }))
  return items
})

const activeItem = computed(() => {
  return flattenedItems.value[activeIndex.value] || null
})

watch(() => props.isOpen, (open) => {
  if (open) {
    query.value = ''
    results.value = { tasks: [], projects: [], modules: [] }
    activeIndex.value = 0
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
})

let searchTimeout = null
watch(query, (val) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!val.trim()) {
    results.value = { tasks: [], projects: [], modules: [] }
    searching.value = false
    activeIndex.value = 0
    return
  }

  searching.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const res = await globalSearch(val)
      results.value = res || { tasks: [], projects: [], modules: [] }
      activeIndex.value = 0
    } catch (e) {
      console.error(e)
    } finally {
      searching.value = false
    }
  }, 200)
})

function close() {
  emit('close')
}

function setActive(item) {
  const idx = flattenedItems.value.findIndex(i => i.id === item.id)
  if (idx !== -1) activeIndex.value = idx
}

function navigateResults(delta) {
  const count = flattenedItems.value.length
  if (count === 0) return
  activeIndex.value = (activeIndex.value + delta + count) % count
}

function selectActiveItem() {
  if (activeItem.value) {
    handleSelect(activeItem.value)
  }
}

function handleSelect(item) {
  close()
  if (item.itemType === 'task') {
    router.push(item.project ? `/projects/${item.project}/tasks/${item.name}` : '/tasks/' + item.name)
  } else if (item.itemType === 'project') {
    router.push('/projects/' + item.name)
  } else if (item.route) {
    router.push(item.route)
  } else if (item.action === 'open-new-task') {
    emit('open-new-task')
  } else if (item.action === 'open-new-project') {
    emit('open-new-project')
  } else if (item.action === 'open-settings') {
    emit('open-settings')
  }
}

// Global Ctrl+K / Cmd+K listener
function handleKeyDown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    if (props.isOpen) {
      close()
    } else {
      // Toggle
      emit('open')
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

