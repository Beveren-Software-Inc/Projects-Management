<template>
  <div>
    <!-- Backdrop overlay covering only the content area beside the sidebar -->
    <div
      v-if="isOpen"
      class="fixed inset-y-0 right-0 z-40 bg-black/20 transition-opacity"
      :style="{ left: sidebarWidth + 'px' }"
      @click="$emit('close')"
    ></div>

    <!-- Notification Flyout Drawer beside Sidebar -->
    <div
      v-if="isOpen"
      class="fixed top-0 bottom-0 z-50 w-96 max-w-[calc(100vw-240px)] bg-surface-white border-r border-outline-gray-2 shadow-xl flex flex-col transition-all duration-200 select-none overflow-hidden"
      :style="{ left: sidebarWidth + 'px' }"
    >
      <!-- 1. Header: Frappe UI Badge, Button, Icon styling -->
      <div class="h-12 px-4 border-b border-outline-gray-2 flex items-center justify-between shrink-0 bg-surface-white">
        <div class="flex items-center gap-2">
          <h2 class="text-base-medium font-medium text-ink-gray-9">Notifications</h2>
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
            icon="lucide-check-check"
            title="Mark all as read"
            :loading="markingAll"
            @click="handleMarkAllAsRead"
          />

          <Button
            variant="ghost"
            size="sm"
            icon="lucide-x"
            title="Close"
            @click="$emit('close')"
          />
        </div>
      </div>

      <!-- 2. Filter Sub-Bar: Frappe UI TabButtons & Select -->
      <div class="px-4 py-2 border-b border-outline-gray-2 flex items-center justify-between bg-surface-gray-1 shrink-0 gap-2">
        <TabButtons
          :options="tabOptions"
          v-model="readFilter"
          size="sm"
          variant="subtle"
        />

        <Select
          :options="categoryOptions"
          v-model="categoryFilter"
          size="sm"
          class="w-36"
        />
      </div>

      <!-- 3. Scrollable Notification List -->
      <div class="flex-1 overflow-y-auto divide-y divide-outline-gray-1 bg-surface-white">
        <!-- Loading State -->
        <div v-if="loading" class="py-16 text-center text-sm text-ink-gray-5 flex items-center justify-center gap-2">
          <Spinner class="w-4 h-4 text-ink-gray-6" />
          <span>Loading notifications...</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredNotifications.length === 0" class="py-20 px-6 text-center">
          <div class="size-10 rounded-full bg-surface-gray-2 text-ink-gray-5 flex items-center justify-center mx-auto mb-3">
            <span class="lucide-bell-off size-5 text-ink-gray-4" />
          </div>
          <div class="text-sm font-medium text-ink-gray-8">No notifications</div>
          <div class="text-xs text-ink-gray-5 mt-1">
            {{ readFilter === 'unread' ? 'You have caught up with all updates!' : 'No notification history found.' }}
          </div>
        </div>

        <!-- Notification Rows -->
        <div
          v-for="item in filteredNotifications"
          :key="item.name"
          @click="handleNotificationClick(item)"
          class="px-4 py-3 cursor-pointer transition-colors flex items-start gap-3 select-none"
          :class="!item.read ? 'bg-surface-gray-2/60 hover:bg-surface-gray-2' : 'hover:bg-surface-gray-1'"
        >
          <!-- Sender Avatar -->
          <Avatar
            :label="item.from_user_name || item.from_user || 'System'"
            :image="item.from_user_image"
            size="md"
            class="shrink-0 mt-0.5"
          />

          <!-- Content Details -->
          <div class="flex-1 min-w-0">
            <div
              class="text-sm text-ink-gray-8 leading-snug break-words"
              :class="{ 'font-medium text-ink-gray-9': !item.read }"
              v-html="cleanSubject(item.subject)"
            ></div>

            <div class="flex items-center gap-2 mt-1 text-xs text-ink-gray-5">
              <span>{{ item.pretty_time || formatDate(item.creation) }}</span>
              <template v-if="item.type">
                <span class="text-ink-gray-3">•</span>
                <Badge size="sm" variant="subtle" theme="gray">{{ cleanTypeName(item.type) }}</Badge>
              </template>
            </div>
          </div>

          <!-- Unread Blue Dot Indicator -->
          <div
            v-if="!item.read"
            class="size-2 rounded-full bg-blue-600 shrink-0 mt-2"
            title="Unread"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Badge,
  Button,
  Avatar,
  TabButtons,
  Select,
  Spinner,
} from 'frappe-ui'
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
} from '../api'

const props = defineProps({
  isOpen: Boolean,
  sidebarWidth: {
    type: Number,
    default: 240,
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

const tabOptions = computed(() => [
  { label: 'All', value: 'all' },
  { label: unreadCount.value > 0 ? `Unread (${unreadCount.value})` : 'Unread', value: 'unread' },
])

const categoryOptions = [
  { label: 'All Categories', value: 'all' },
  { label: 'Assignments', value: 'Assignment' },
  { label: 'Mentions', value: 'Mention' },
  { label: 'Status Updates', value: 'Status Change' },
  { label: 'Reopened Tasks', value: 'Ticket Reopened' },
]

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

async function handleNotificationClick(item) {
  if (!item.read) {
    try {
      await markNotificationRead(item.name)
      item.read = 1
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      emit('count-changed', unreadCount.value)
    } catch (e) {}
  }

  emit('close')

  if (item.document_type === 'Task' && item.document_name) {
    router.push('/tasks/' + item.document_name)
  } else if (item.document_type === 'Project' && item.document_name) {
    router.push('/projects/' + item.document_name)
  } else if (item.document_type === 'HD Ticket' && item.document_name) {
    router.push('/tasks')
  }
}

async function handleMarkAllAsRead() {
  markingAll.value = true
  try {
    await markAllNotificationsRead()
    notifications.value.forEach((n) => { n.read = 1 })
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
  return sub
    .replace(/ticket\s*#?/gi, 'task #')
    .replace(/Ticket\s*#?/gi, 'Task #')
    .replace(/HD\s*Ticket/gi, 'Task')
    .replace(/reopened\s+task/gi, 'reopened task')
}

function cleanTypeName(type) {
  if (!type) return ''
  if (type === 'Ticket Reopened') return 'Task Reopened'
  if (type === 'HD Ticket') return 'Task'
  return type
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
