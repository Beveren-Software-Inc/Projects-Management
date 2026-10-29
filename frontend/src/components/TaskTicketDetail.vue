<template>
  <section class="surface-panel task-detail-panel">
    <div class="detail-toolbar">
      <div>
        <span class="panel-kicker">TASK DETAILS</span>
        <span class="detail-context">
          {{ projectLabel || task.project_title || 'Project' }}
          <Icon name="chevron-right" :size="11" />
          {{ moduleLabel || task.module_title || 'Module' }}
        </span>
      </div>
      <div class="detail-actions">
        <button type="button" class="icon-button" aria-label="Copy task link" @click="copyLink">
          <Icon name="share" :size="15" />
        </button>
      </div>
    </div>

    <div ref="threadRef" class="detail-scroll">
      <div class="detail-title-row">
        <button
          type="button"
          class="detail-complete-toggle"
          :class="{ 'is-complete': task.status === 'Completed' }"
          @click="updateStatus(task.status === 'Completed' ? 'Open' : 'Completed')"
        >
          <Icon :name="task.status === 'Completed' ? 'check-circle' : 'circle'" :size="21" />
        </button>
        <div class="detail-title-copy">
          <span class="task-id">{{ task.name }}</span>
          <input
            class="detail-title-input"
            :class="{ 'is-complete': task.status === 'Completed' }"
            :value="task.subject || ''"
            @change="event => saveSubject(event.target.value)"
          />
        </div>
      </div>

      <div class="detail-status-row">
        <span class="status-pill status-pill-large" :class="statusClass(task.status)"><span />{{ statusLabel(task.status) }}</span>
        <span v-if="isOverdue" class="overdue-callout"><Icon name="alert-circle" :size="12" /> Past due</span>
        <span class="priority-chip" :class="'priority-' + String(task.priority || 'Medium').toLowerCase()">
          <Icon name="flag" :size="12" /> {{ task.priority || 'Medium' }} priority
        </span>
      </div>

      <div class="detail-properties">
        <label class="detail-property">
          <span>Assignee</span>
          <span class="select-wrap assignee-select">
            <select :value="task.assignee_emails?.[0] || ''" @change="setAssignee($event.target.value)">
              <option value="">Unassigned</option>
              <option v-for="user in availableUsers" :key="user.name" :value="user.name">
                {{ user.full_name || user.name }}
              </option>
            </select>
            <Icon name="chevron-down" :size="14" />
          </span>
        </label>
        <label class="detail-property">
          <span>Due date</span>
          <span class="select-wrap">
            <input class="property-date" type="date" :value="cleanDate(task.exp_end_date)" @change="handleGenericUpdate('exp_end_date', $event.target.value || null)" />
          </span>
        </label>
        <label class="detail-property">
          <span>Status</span>
          <span class="select-wrap">
            <select :value="task.status || 'Open'" @change="updateStatus($event.target.value)">
              <option value="Open">To do</option>
              <option value="Working">In progress</option>
              <option value="Pending Review">In review</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
            <Icon name="chevron-down" :size="14" />
          </span>
        </label>
        <label class="detail-property">
          <span>Priority</span>
          <span class="select-wrap">
            <select :value="task.priority || 'Medium'" @change="handleGenericUpdate('priority', $event.target.value)">
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
              <option>Urgent</option>
            </select>
            <Icon name="chevron-down" :size="14" />
          </span>
        </label>
      </div>

      <section class="detail-section description-section">
        <div class="section-heading-line">
          <h3>Description</h3>
        </div>
        <textarea
          class="description-editor"
          rows="3"
          placeholder="Add the notes for this task."
          :value="task.description || ''"
          @change="handleGenericUpdate('description', $event.target.value)"
        />
      </section>

      <div v-if="(task.files || []).length" class="task-attachment-summary">
        <Icon name="paperclip" :size="14" />
        <strong>{{ task.files.length }} attachments</strong>
        <a :href="task.files[0].file_url" target="_blank">{{ task.files[0].file_name }}</a>
        <span v-if="task.files.length > 1" class="attachment-more">+{{ task.files.length - 1 }}</span>
      </div>
      <label class="add-workstream" style="margin-top: 0">
        <Icon name="paperclip" :size="14" />
        Attach to task
        <input type="file" class="hidden" multiple @change="onTaskFiles" />
      </label>

      <section class="detail-section activity-section">
        <div class="section-heading-line">
          <div class="activity-heading-copy">
            <h3>Activity</h3>
            <span>{{ messageCount }}</span>
          </div>
          <button type="button" class="activity-filter" @click="commentsOnly = !commentsOnly">
            <Icon name="list-filter" :size="12" />
            {{ commentsOnly ? 'Comments' : 'All activity' }}
          </button>
        </div>
        <template v-for="item in visibleActivity" :key="item.id">
          <div v-if="!isMessage(item)" class="activity-event">
            <span class="activity-timeline-dot"><Icon name="check" :size="10" /></span>
            <div class="activity-event-copy">
              <p><strong>{{ item.sender_name || 'System' }}</strong> {{ item.content }}</p>
              <span>{{ formatDateTime(item.timestamp) }}</span>
            </div>
          </div>
          <article v-else class="comment-item">
            <span class="avatar avatar-small" :class="avatarTone(item.sender_name || item.sender)">
              {{ initials(item.sender_name || item.sender) }}
            </span>
            <div class="comment-content">
              <div class="comment-byline">
                <strong>{{ isMine(item) ? 'You' : (item.sender_name || item.sender || 'Someone') }}</strong>
                <span>{{ formatDateTime(item.timestamp) }}</span>
              </div>
              <p v-if="item.content">{{ item.content }}</p>
              <p v-for="file in item.files || []" :key="file.name">
                <a :href="file.file_url" target="_blank">{{ file.file_name }}</a>
              </p>
            </div>
          </article>
        </template>
        <p v-if="!visibleActivity.length" class="description-editor">No messages yet. Write the first note below.</p>
      </section>

      <section v-if="(task.subtasks || []).length" class="detail-section checklist-section">
        <div class="section-heading-line">
          <div class="checklist-heading-copy">
            <h3>Implementation checklist</h3>
            <span>{{ doneSubtasks }} of {{ task.subtasks.length }} complete</span>
          </div>
        </div>
        <div class="checklist-progress-track">
          <span :style="{ width: checklistProgress + '%' }" />
        </div>
        <ul class="checklist-items">
          <li v-for="child in task.subtasks" :key="child.name">
            <button
              type="button"
              class="checklist-checkbox"
              :class="{ 'is-checked': child.status === 'Completed' }"
              @click="toggleSubtask(child)"
            >
              <Icon v-if="child.status === 'Completed'" name="check" :size="10" />
            </button>
            <span :class="{ 'checklist-done': child.status === 'Completed' }" @click="openRelated(child.name)">{{ child.subject }}</span>
          </li>
        </ul>
      </section>
    </div>

    <div v-if="showMentionMenu" class="mention-menu">
      <button
        v-for="(user, index) in mentionUsers"
        :key="user.name"
        type="button"
        :class="{ 'is-active': index === mentionIndex }"
        @mousedown.prevent="selectMention(user)"
      >
        {{ user.full_name || user.name }}
      </button>
      <div v-if="!mentionUsers.length" class="px-3 py-2 text-xs">No matching people</div>
    </div>
    <div v-if="pendingFiles.length" class="task-attachment-summary" style="margin: 0 16px 8px">
      <span v-for="(file, index) in pendingFiles" :key="file.name + index">
        {{ file.name }}
        <button type="button" @click="pendingFiles.splice(index, 1)">×</button>
      </span>
    </div>
    <form class="comment-composer" @submit.prevent="submitComment">
      <span class="avatar avatar-small avatar-indigo">{{ initials(myName) }}</span>
      <textarea
        ref="commentInput"
        v-model="commentDraft"
        rows="2"
        placeholder="Write a comment or use @ to mention someone"
        @input="onCommentInput"
        @keydown="onCommentKeydown"
      />
      <label class="icon-button" title="Attach files">
        <Icon name="paperclip" :size="15" />
        <input type="file" class="hidden" multiple @change="onCommentFiles" />
      </label>
      <button type="submit" class="comment-send" aria-label="Send comment" :disabled="(!commentDraft.trim() && !pendingFiles.length) || commentSending">
        <Icon name="send" :size="14" />
      </button>
    </form>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Icon from './Icon.vue'
import { sessionUserName } from '@/sessionUser'
import {
  addTaskComment,
  assignTask,
  getTask,
  getUsers,
  updateTask,
  uploadFile,
} from '../api'

const props = defineProps({
  taskId: { type: String, required: true },
  showBack: { type: Boolean, default: true },
  showClose: { type: Boolean, default: false },
  projectLabel: { type: String, default: '' },
  moduleLabel: { type: String, default: '' },
})

const emit = defineEmits(['back', 'close', 'updated'])
const router = useRouter()

const task = ref({})
const availableUsers = ref([])
const commentDraft = ref('')
const commentSending = ref(false)
const commentInput = ref(null)
const threadRef = ref(null)
const pendingFiles = ref([])
const showMentionMenu = ref(false)
const mentionQuery = ref('')
const mentionIndex = ref(0)
const pickedMentions = ref([])
const commentsOnly = ref(false)
const myName = computed(() => sessionUserName())

const activityFeed = computed(() => {
  return [...(task.value.activity_timeline || [])].sort((a, b) =>
    String(a.timestamp || '').localeCompare(String(b.timestamp || ''))
  )
})

const visibleActivity = computed(() => {
  if (!commentsOnly.value) return activityFeed.value
  return activityFeed.value.filter(item => isMessage(item))
})

const messageCount = computed(() => activityFeed.value.filter(item => isMessage(item)).length)

const doneSubtasks = computed(() => (task.value.subtasks || []).filter(child => child.status === 'Completed').length)

const checklistProgress = computed(() => {
  const total = (task.value.subtasks || []).length
  if (!total) return 0
  return Math.round((doneSubtasks.value / total) * 100)
})

const isOverdue = computed(() => {
  if (!task.value.exp_end_date) return false
  if (task.value.status === 'Completed' || task.value.status === 'Cancelled') return false
  return cleanDate(task.value.exp_end_date) < new Date().toISOString().slice(0, 10)
})

const mentionUsers = computed(() => {
  const query = mentionQuery.value.toLowerCase()
  return availableUsers.value.filter(user => {
    if (!query) return true
    return (user.full_name || '').toLowerCase().includes(query) || (user.name || '').toLowerCase().includes(query)
  }).slice(0, 8)
})

const statusOptions = computed(() => [
  { label: 'Open', onClick: () => updateStatus('Open') },
  { label: 'Working', onClick: () => updateStatus('Working') },
  { label: 'Pending Review', onClick: () => updateStatus('Pending Review') },
  { label: 'Completed', onClick: () => updateStatus('Completed') },
  { label: 'Cancelled', onClick: () => updateStatus('Cancelled') },
])

onMounted(async () => {
  await Promise.all([loadTask(), loadMetadata()])
})

watch(() => props.taskId, () => {
  commentDraft.value = ''
  pendingFiles.value = []
  pickedMentions.value = []
  showMentionMenu.value = false
  loadTask()
})

async function loadMetadata() {
  try {
    availableUsers.value = (await getUsers()) || []
  } catch (error) {
    console.error(error)
  }
}

function openRelated(taskId) {
  if (!taskId) return
  if (task.value.project) {
    router.push(`/projects/${task.value.project}/tasks/${taskId}`)
    return
  }
  router.push('/tasks/' + taskId)
}

async function loadTask() {
  if (!props.taskId) return
  try {
    task.value = await getTask(props.taskId)
    await nextTick()
    if (threadRef.value) threadRef.value.scrollTop = threadRef.value.scrollHeight
  } catch (error) {
    console.error(error)
  }
}

async function handleGenericUpdate(fieldName, value) {
  try {
    await updateTask(task.value.name, { [fieldName]: value })
    task.value[fieldName] = value
    await loadTask()
    emit('updated')
  } catch (error) {
    alert(`Could not update ${fieldName}`)
  }
}

async function saveSubject(value) {
  const subject = value.trim()
  if (!subject || subject === task.value.subject) return
  await handleGenericUpdate('subject', subject)
}

async function updateStatus(status) {
  await handleGenericUpdate('status', status)
  if (status === 'Completed') task.value.progress = 100
}

async function setAssignee(email) {
  try {
    task.value = await assignTask(task.value.name, email, 'set')
    emit('updated')
  } catch (error) {
    alert('Could not update the assignee')
  }
}

async function toggleSubtask(child) {
  const status = child.status === 'Completed' ? 'Open' : 'Completed'
  try {
    await updateTask(child.name, { status })
    await loadTask()
    emit('updated')
  } catch (error) {
    alert('Could not update the subtask')
  }
}

function onCommentFiles(event) {
  pendingFiles.value.push(...Array.from(event.target.files || []))
  event.target.value = ''
}

async function onTaskFiles(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  if (!files.length || !task.value.name) return
  try {
    for (const file of files) {
      await uploadFile('Task', task.value.name, file)
    }
    await loadTask()
    emit('updated')
  } catch (error) {
    alert('Could not upload the file')
  }
}

function onCommentInput() {
  const cursor = commentInput.value?.selectionStart || 0
  const before = commentDraft.value.slice(0, cursor)
  const at = before.lastIndexOf('@')
  if (at !== -1 && (at === 0 || /\s/.test(before[at - 1]))) {
    const query = before.slice(at + 1)
    if (!/\s/.test(query)) {
      mentionQuery.value = query
      mentionIndex.value = 0
      showMentionMenu.value = true
      return
    }
  }
  showMentionMenu.value = false
}

function onCommentKeydown(event) {
  if (!showMentionMenu.value) return
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    mentionIndex.value = (mentionIndex.value + 1) % Math.max(mentionUsers.value.length, 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    mentionIndex.value = (mentionIndex.value - 1 + mentionUsers.value.length) % Math.max(mentionUsers.value.length, 1)
  } else if (event.key === 'Enter' && mentionUsers.value.length) {
    event.preventDefault()
    selectMention(mentionUsers.value[mentionIndex.value])
  } else if (event.key === 'Escape') {
    showMentionMenu.value = false
  }
}

function selectMention(user) {
  if (!user) return
  const cursor = commentInput.value?.selectionStart || commentDraft.value.length
  const before = commentDraft.value.slice(0, cursor)
  const at = before.lastIndexOf('@')
  const label = user.full_name || user.name
  if (at !== -1) {
    commentDraft.value = before.slice(0, at) + `@${label} ` + commentDraft.value.slice(cursor)
  }
  if (!pickedMentions.value.some(person => person.email === user.name)) {
    pickedMentions.value.push({ email: user.name, label })
  }
  showMentionMenu.value = false
  nextTick(() => commentInput.value?.focus())
}

function commentHtml(text) {
  let html = escapeHtml(text)
  const people = [...pickedMentions.value].sort((a, b) => b.label.length - a.label.length)
  for (const person of people) {
    const token = escapeHtml(`@${person.label}`)
    const span = `<span class="mention" data-id="${escapeHtml(person.email)}" data-value="${escapeHtml(person.label)}">@${escapeHtml(person.label)}</span>`
    html = html.split(token).join(span)
  }
  return html.replace(/\n/g, '<br>')
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function isMessage(item) {
  return item.type === 'comment' || item.type === 'communication'
}

function isMine(item) {
  return Boolean(window.session_user) && item.sender === window.session_user
}

async function submitComment() {
  const text = commentDraft.value.trim()
  const files = [...pendingFiles.value]
  if ((!text && !files.length) || !task.value.name) return
  const content = text || files.map(file => file.name).join(', ')
  commentSending.value = true
  try {
    const saved = await addTaskComment(task.value.name, commentHtml(content))
    for (const file of files) {
      await uploadFile('Comment', saved.id, file)
    }
    commentDraft.value = ''
    pendingFiles.value = []
    pickedMentions.value = []
    showMentionMenu.value = false
    await loadTask()
    emit('updated')
  } catch (error) {
    alert('Could not send the message')
  } finally {
    commentSending.value = false
  }
}

function cleanDate(dateStr) {
  if (!dateStr) return ''
  return String(dateStr).split(' ')[0]
}

function statusLabel(status) {
  if (status === 'Working') return 'In progress'
  if (status === 'Pending Review') return 'In review'
  if (status === 'Open') return 'To do'
  return status || 'To do'
}

function avatarTone(name) {
  const tones = ['avatar-indigo', 'avatar-coral', 'avatar-teal', 'avatar-lilac', 'avatar-amber']
  let total = 0
  for (const char of String(name || '')) total += char.charCodeAt(0)
  return tones[total % tones.length]
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(window.location.href)
  } catch (error) {
    console.error(error)
  }
}

function statusClass(status) {
  if (status === 'Completed') return 'status-completed'
  if (status === 'Working') return 'status-in-progress'
  if (status === 'Pending Review') return 'status-in-review'
  return 'status-to-do'
}

function initials(name) {
  const parts = String(name || '?').trim().split(/\s+/).slice(0, 2)
  return parts.map(part => part[0]?.toUpperCase() || '').join('') || '?'
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(String(dateStr).replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return String(dateStr)
  return date.toLocaleString(undefined, {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}
</script>
