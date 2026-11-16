<template>
  <!-- Activity feed laid out like Helpdesk's TicketAgentActivities: icon rail + connecting line + entries -->
  <div v-if="activities.length" class="activities">
    <div
      v-for="(activity, i) in activities"
      :key="activity.key"
      class="activity grid grid-cols-[30px_minmax(auto,_1fr)] gap-2 sm:gap-4"
    >
      <!-- Icon rail -->
      <div
        class="relative flex justify-center after:absolute after:left-1/2 after:top-0 after:border-l after:border-outline-gray-2"
        :class="i !== activities.length - 1 ? 'after:h-full' : 'after:h-4'"
      >
        <div
          class="relative z-10 flex h-7 w-7 items-center justify-center rounded-full bg-surface-white text-ink-gray-7"
        >
          <EmailIcon v-if="activity.type === 'email'" class="size-4" />
          <CommentIcon v-else-if="activity.type === 'comment'" class="size-4" />
          <ActivityIcon v-else-if="activity.type === 'description'" class="size-4" />
          <span v-else class="h-1.5 w-1.5 rounded-full bg-ink-gray-4"></span>
        </div>
      </div>

      <!-- EMAIL (Helpdesk EmailArea) -->
      <div v-if="activity.type === 'email'" class="mb-4 min-w-0">
        <div class="rounded-lg border border-outline-gray-1 bg-surface-white p-3 shadow-sm text-base">
          <div class="mb-1 flex items-center justify-between gap-2">
            <div class="flex min-w-0 items-center gap-2">
              <Avatar size="md" :label="activity.userName" :image="activity.userImage" />
              <span class="truncate font-medium text-ink-gray-8">{{ activity.userName }}</span>
              <span class="hidden truncate text-sm text-ink-gray-5 sm:inline">&lt;{{ activity.user }}&gt;</span>
            </div>
            <div class="flex shrink-0 items-center gap-1">
              <Tooltip :text="fullDate(activity.timestamp)">
                <span class="text-sm text-ink-gray-5">{{ timeAgo(activity.timestamp) }}</span>
              </Tooltip>
              <Tooltip text="Reply">
                <Button variant="ghost" size="sm" class="text-ink-gray-7" @click="$emit('reply', activity, false)">
                  <template #icon>
                    <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 17 4 12 9 7" /><path d="M20 18v-2a4 4 0 0 0-4-4H4" /></svg>
                  </template>
                </Button>
              </Tooltip>
              <Tooltip text="Reply all">
                <Button variant="ghost" size="sm" class="text-ink-gray-7" @click="$emit('reply', activity, true)">
                  <template #icon>
                    <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 17 2 12 7 7" /><polyline points="12 17 7 12 12 7" /><path d="M22 18v-2a4 4 0 0 0-4-4H7" /></svg>
                  </template>
                </Button>
              </Tooltip>
            </div>
          </div>
          <div v-if="activity.recipients" class="mb-2 truncate text-sm text-ink-gray-5">
            To: {{ activity.recipients }}
          </div>
          <div v-if="activity.subject" class="mb-1 text-p-base font-medium text-ink-gray-8">{{ activity.subject }}</div>
          <div class="timeline-html text-p-base text-ink-gray-7" v-html="activity.content"></div>
        </div>
      </div>

      <!-- COMMENT / TASK DESCRIPTION (Helpdesk CommentBox) -->
      <div v-else-if="activity.type === 'comment' || activity.type === 'description'" class="mb-4 min-w-0 text-base">
        <div class="mb-1 ml-0.5 flex items-center justify-between gap-2">
          <div class="flex min-w-0 items-center gap-2 text-ink-gray-5">
            <Avatar size="md" :label="activity.userName" :image="activity.userImage" />
            <p class="truncate">
              <span class="font-medium text-ink-gray-8">{{ activity.userName }}</span>
              <template v-if="activity.type === 'comment'">
                <span class="ms-1">added a</span>
                <span class="ms-1 font-medium text-ink-gray-8">comment</span>
              </template>
              <span v-else class="ms-1">created this task</span>
            </p>
          </div>
          <div class="flex shrink-0 items-center gap-1">
            <Tooltip :text="fullDate(activity.timestamp)">
              <span class="text-sm text-ink-gray-5">{{ timeAgo(activity.timestamp) }}</span>
            </Tooltip>
            <Dropdown
              v-if="activity.type === 'comment' && canModify(activity) && editingKey !== activity.key"
              :options="commentOptions(activity)"
              align="end"
            >
              <Button variant="ghost" size="sm" class="text-ink-gray-6">
                <template #icon>
                  <Icon name="more-horizontal" size="15" />
                </template>
              </Button>
            </Dropdown>
          </div>
        </div>

        <!-- Inline edit (own comments) -->
        <div v-if="editingKey === activity.key" class="rounded-lg border border-outline-gray-2 bg-surface-white p-2">
          <textarea
            ref="editRef"
            v-model="editText"
            rows="4"
            class="w-full resize-y border-0 bg-transparent p-1 text-p-base text-ink-gray-8 focus:outline-none focus:ring-0"
            @keydown.esc="cancelEdit"
            @keydown.ctrl.enter="saveEdit(activity)"
            @keydown.meta.enter="saveEdit(activity)"
          ></textarea>
          <div class="flex justify-end gap-2 pt-1">
            <Button variant="subtle" size="sm" label="Cancel" @click="cancelEdit" />
            <Button variant="solid" size="sm" label="Save" :loading="saving" @click="saveEdit(activity)" />
          </div>
        </div>
        <div
          v-else
          class="rounded-lg border border-outline-gray-1 bg-surface-gray-1 px-4 py-3"
        >
          <div
            v-if="activity.content"
            class="timeline-html text-p-base text-ink-gray-7"
            v-html="activity.content"
          ></div>
          <div v-else class="text-p-base italic text-ink-gray-4">No description added for this task.</div>
        </div>
      </div>

      <!-- HISTORY (Helpdesk HistoryBox) -->
      <div v-else class="mb-4 flex min-w-0 items-center justify-between gap-2 pt-1.5 text-base">
        <div class="min-w-0 text-p-base text-ink-gray-5">
          <span class="font-medium text-ink-gray-8">{{ activity.userName }}</span>
          <span class="ms-1">{{ activity.action }}</span>
        </div>
        <Tooltip :text="fullDate(activity.timestamp)">
          <span class="shrink-0 text-sm text-ink-gray-5">{{ timeAgo(activity.timestamp) }}</span>
        </Tooltip>
      </div>
    </div>
  </div>

  <!-- Empty state (Helpdesk style) -->
  <div
    v-else
    class="flex flex-1 flex-col items-center justify-center gap-2 py-20 text-base font-medium text-ink-gray-4"
  >
    <EmailIcon v-if="emptyIcon === 'email'" class="h-10 w-10" />
    <CommentIcon v-else-if="emptyIcon === 'comment'" class="h-10 w-10" />
    <ActivityIcon v-else class="h-10 w-10" />
    <span>{{ emptyText }}</span>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { Avatar, Button, Dropdown, Tooltip, toast } from 'frappe-ui'
import Icon from './Icon.vue'
import ActivityIcon from './icons/ActivityIcon.vue'
import EmailIcon from './icons/EmailIcon.vue'
import CommentIcon from './icons/CommentIcon.vue'
import { editTaskComment, deleteTaskComment } from '../api'

defineProps({
  activities: { type: Array, default: () => [] },
  emptyText: { type: String, default: 'No activities' },
  emptyIcon: { type: String, default: 'activity' },
})

const emit = defineEmits(['reply', 'comment-updated', 'comment-deleted'])

const currentUser = window.session_user || window.user_info?.email || ''

function canModify(activity) {
  return activity.user && activity.user === currentUser
}

// ---- Edit / delete own comments ----
const editingKey = ref(null)
const editText = ref('')
const editRef = ref(null)
const saving = ref(false)

function commentOptions(activity) {
  return [
    { label: 'Edit', onClick: () => startEdit(activity) },
    { label: 'Delete', onClick: () => removeComment(activity) },
  ]
}

function htmlToText(html) {
  const el = document.createElement('div')
  el.innerHTML = (html || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>\s*<p[^>]*>/gi, '\n\n')
  return (el.textContent || '').trim()
}

async function startEdit(activity) {
  editingKey.value = activity.key
  editText.value = htmlToText(activity.content)
  await nextTick()
  const el = Array.isArray(editRef.value) ? editRef.value[0] : editRef.value
  el?.focus()
}

function cancelEdit() {
  editingKey.value = null
  editText.value = ''
}

async function saveEdit(activity) {
  if (!editText.value.trim()) return
  saving.value = true
  try {
    const res = await editTaskComment(activity.id, editText.value)
    emit('comment-updated', activity.id, res?.content)
    toast.success('Comment updated')
    cancelEdit()
  } catch (e) {
    toast.error('Failed to update comment: ' + (e.message || e))
  } finally {
    saving.value = false
  }
}

async function removeComment(activity) {
  if (!confirm('Delete this comment?')) return
  try {
    await deleteTaskComment(activity.id)
    emit('comment-deleted', activity.id)
    toast.success('Comment deleted')
  } catch (e) {
    toast.error('Failed to delete comment: ' + (e.message || e))
  }
}

// ---- Dates ----
function toDate(value) {
  if (!value) return null
  const d = new Date(String(value).replace(' ', 'T'))
  return isNaN(d.getTime()) ? null : d
}

function timeAgo(value) {
  const d = toDate(value)
  if (!d) return ''
  const secs = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000))
  if (secs < 60) return 'just now'
  const units = [
    ['year', 31536000],
    ['month', 2592000],
    ['week', 604800],
    ['day', 86400],
    ['hour', 3600],
    ['minute', 60],
  ]
  for (const [unit, size] of units) {
    const n = Math.floor(secs / size)
    if (n >= 1) return `${n} ${unit}${n > 1 ? 's' : ''} ago`
  }
  return 'just now'
}

function fullDate(value) {
  const d = toDate(value)
  if (!d) return ''
  return d.toLocaleString('en-GB', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
