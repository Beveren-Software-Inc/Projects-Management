<template>
  <div>
    <!-- Backdrop overlay to dismiss on outside click -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm transition-opacity"
      @click="$emit('close')"
    ></div>

    <!-- Notification Flyout Drawer beside Sidebar -->
    <div
      v-if="isOpen"
      class="fixed top-0 bottom-0 z-50 w-[360px] min-w-[360px] max-w-[360px] !bg-white border-r border-outline-gray-2 shadow-2xl flex flex-col transition-transform duration-200 select-none rounded-r-2xl overflow-hidden"
      :style="{ left: sidebarWidth + 'px' }"
    >
      <!-- 1. Header matching Helpdesk -->
      <div class="px-4 pt-4 pb-3 border-b border-outline-gray-1 flex items-center justify-between shrink-0 !bg-white">
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-semibold text-ink-gray-9">Notifications</h2>
          <Badge
            v-if="unreadCount > 0"
            theme="blue"
            variant="subtle"
            size="sm"
            :label="unreadCount"
          />
        </div>

        <div class="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            class="!p-1.5 text-ink-gray-5 hover:text-ink-gray-8 rounded-xl"
            title="Mark all as read"
            :loading="markingAll"
            @click="handleMarkAllAsRead"
          >
            <template #prefix>
              <Icon name="check-check" size="14" />
            </template>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            class="!p-1.5 text-ink-gray-5 hover:text-ink-gray-8 rounded-xl"
            title="Close"
            @click="$emit('close')"
          >
            <template #prefix>
              <Icon name="x" size="14" />
            </template>
          </Button>
        </div>
      </div>

      <!-- 2. Filter Sub-Bar (All vs Unread & Category) -->
      <div class="px-4 py-2 border-b border-outline-gray-1 flex items-center justify-between bg-surface-gray-1 shrink-0 text-xs">
        <!-- Read Filter Tabs -->
        <div class="flex items-center p-0.5 bg-surface-gray-2 rounded-xl border border-outline-gray-2">
          <button
            @click="readFilter = 'all'"
            class="px-2.5 py-1 rounded-lg text-xs transition"
            :class="readFilter === 'all' ? 'bg-surface-white font-semibold text-ink-gray-9 shadow-2xs' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          >
            All
          </button>
          <button
            @click="readFilter = 'unread'"
            class="px-2.5 py-1 rounded-lg text-xs transition flex items-center gap-1"
            :class="readFilter === 'unread' ? 'bg-surface-white font-semibold text-ink-gray-9 shadow-2xs' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          >
            <span>Unread</span>
            <span v-if="unreadCount > 0" class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          </button>
        </div>

        <!-- Category Dropdown -->
        <select
          v-model="categoryFilter"
          class="px-3 py-1 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white text-ink-gray-7 focus:outline-none transition shadow-2xs cursor-pointer"
        >
          <option value="all">All categories</option>
          <option value="Assignment">Assignments</option>
          <option value="Mention">Mentions</option>
          <option value="Ticket Reopened">Reopened</option>
        </select>
      </div>

      <!-- 3. Scrollable Notification List -->
      <div class="flex-1 overflow-y-auto p-2 space-y-1 !bg-white">
        <div v-if="loading" class="py-16 text-center text-xs text-ink-gray-4 flex items-center justify-center gap-2">
          <Icon name="refresh" size="14" class="animate-spin text-ink-gray-6" />
          <span>Loading notifications...</span>
        </div>

        <div v-else-if="filteredNotifications.length === 0" class="py-16 px-6 text-center text-xs text-ink-gray-4">
          <Icon name="bell-off" size="24" class="mx-auto text-ink-gray-3 mb-2" />
          <div class="font-medium text-ink-gray-6">No notifications</div>
          <div class="text-[11px] text-ink-gray-4 mt-0.5">
            {{ readFilter === 'unread' ? 'You have caught up with all updates!' : 'No notification history found.' }}
          </div>
        </div>

        <div
          v-for="item in filteredNotifications"
          :key="item.name"
          @click="handleNotificationClick(item)"
          class="p-3 rounded-xl hover:bg-surface-gray-1 cursor-pointer transition flex items-start gap-3 select-none"
          :class="{ 'bg-blue-50/30': !item.read }"
        >
          <!-- Sender Avatar -->
          <Avatar
            :label="item.from_user_name || item.from_user || 'System'"
            :image="item.from_user_image"
            size="md"
            class="shrink-0 mt-0.5"
          />

          <!-- Content Details -->
          <div class="flex-1 min-w-0 space-y-1">
            <div
              class="text-xs text-ink-gray-8 leading-snug line-clamp-2"
              v-html="cleanSubject(item.subject)"
            ></div>

            <div class="flex items-center justify-between text-[11px] text-ink-gray-4">
              <span>{{ item.pretty_time || formatDate(item.creation) }}</span>
              <span v-if="item.type" class="text-ink-gray-5 font-medium">{{ item.type }}</span>
            </div>
          </div>

          <!-- Unread Blue Dot -->
          <div v-if="!item.read" class="w-2 h-2 rounded-full bg-blue-600 shrink-0 mt-1.5"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Badge, Button, Avatar } from 'frappe-ui'
import Icon from './Icon.vue'
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
} from '../api'

const props = defineProps({
  isOpen: Boolean,
  sidebarWidth: {
    type: Number,
    default: 220,
  },
})

const emit = defineEmits(['close', 'count-changed'])

const router = useRouter()
const loading = ref(false)
const markingAll = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const readFilter = ref('all')
const categoryFilter = ref('all')

const filteredNotifications = computed(() => {
  return notifications.value.filter((n) => {
    // 1. Read filter
    if (readFilter.value === 'unread' && n.read) return false

    // 2. Category filter
    if (categoryFilter.value !== 'all' && n.type !== categoryFilter.value) return false

    return true
  })
})

onMounted(async () => {
  await fetchNotifications()
})

watch(() => props.isOpen, (open) => {
  if (open) {
    fetchNotifications()
  }
})

async function fetchNotifications() {
  loading.value = true
  try {
    const res = await getNotifications(40)
    notifications.value = res?.notifications || []
    unreadCount.value = res?.unread_count || 0
    emit('count-changed', unreadCount.value)
  } catch (e) {
    console.error('Failed to load notifications', e)
  } finally {
    loading.value = false
  }
}

async function handleNotificationClick(n) {
  if (!n.read) {
    try {
      await markNotificationRead(n.name)
      n.read = 1
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      emit('count-changed', unreadCount.value)
    } catch (e) {}
  }

  emit('close')

  // Route to relevant document if matching Task or Project
  if (n.document_type === 'Task' && n.document_name) {
    router.push('/tasks/' + n.document_name)
  } else if (n.document_type === 'Project' && n.document_name) {
    router.push('/projects/' + n.document_name)
  } else if (n.document_type === 'HD Ticket' && n.document_name) {
    router.push('/tasks')
  }
}

async function handleMarkAllAsRead() {
  markingAll.value = true
  try {
    await markAllNotificationsRead()
    notifications.value.forEach(n => { n.read = 1 })
    unreadCount.value = 0
    emit('count-changed', 0)
  } catch (e) {
    console.error('Failed to mark all as read', e)
  } finally {
    markingAll.value = false
  }
}

function cleanSubject(sub) {
  if (!sub) return ''
  // Strip external cloud links if any, keep strong tags
  return sub
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

