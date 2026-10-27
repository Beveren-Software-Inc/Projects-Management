<template>
  <div class="!bg-white rounded-2xl border border-outline-gray-2 shadow-sm overflow-hidden select-none transition-all">
    <!-- 1. Top Mode Switcher & Collapsed Action Bar -->
    <div class="px-4 py-2.5 flex items-center justify-between !bg-white">
      <div class="flex items-center gap-1.5">
        <button
          type="button"
          @click="toggleMode('reply')"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition cursor-pointer"
          :class="!isCollapsed && activeMode === 'reply'
            ? 'bg-surface-gray-3 text-ink-gray-9 font-semibold shadow-2xs'
            : 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-gray-2'"
        >
          <EmailIcon class="size-3.5 text-ink-gray-7" />
          <span>Reply</span>
        </button>

        <button
          type="button"
          @click="toggleMode('comment')"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition cursor-pointer"
          :class="!isCollapsed && activeMode === 'comment'
            ? 'bg-surface-gray-3 text-ink-gray-9 font-semibold shadow-2xs'
            : 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-gray-2'"
        >
          <CommentIcon class="size-3.5 text-ink-gray-7" />
          <span>Comment</span>
        </button>
      </div>

      <!-- Collapsed hint -->
      <div
        v-if="isCollapsed"
        @click="toggleMode('reply')"
        class="flex items-center gap-1.5 text-xs text-ink-gray-4 hover:text-ink-gray-7 cursor-pointer transition select-none"
      >
        <span>Write a reply or comment...</span>
        <Icon name="chevron-down" size="12" />
      </div>

      <!-- Collapse button when expanded -->
      <button
        v-else
        type="button"
        @click="isCollapsed = true"
        class="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs text-ink-gray-5 hover:text-ink-gray-9 hover:bg-surface-gray-2 transition cursor-pointer"
        title="Collapse editor"
      >
        <span class="text-[11px] font-medium">Collapse</span>
        <Icon name="chevron-down" size="12" class="rotate-180" />
      </button>
    </div>

    <!-- 2. Expandable Editor Body -->
    <div v-show="!isCollapsed" class="border-t border-outline-gray-1">
      <!-- Email Header Rows (Only in Reply Mode - Matching Screenshot 1) -->
      <div v-if="activeMode === 'reply'" class="!bg-white border-b border-outline-gray-1 text-xs">
      <!-- To Row -->
      <div class="px-4 py-2 flex items-center gap-2">
        <span class="text-ink-gray-4 shrink-0 w-8">To:</span>
        <div class="flex-1 flex flex-wrap items-center gap-1.5 min-w-0">
          <!-- Recipient Chips -->
          <span
            v-for="email in toRecipients"
            :key="email"
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-gray-2 text-ink-gray-8 text-xs border border-outline-gray-2"
          >
            <span>{{ email }}</span>
            <button
              type="button"
              @click="removeRecipient(email)"
              class="text-ink-gray-4 hover:text-ink-gray-9 text-xs leading-none"
            >
              ×
            </button>
          </span>

          <!-- Inline Input for new email -->
          <input
            v-model="newRecipientInput"
            @keydown.enter.prevent="addRecipient"
            @keydown.comma.prevent="addRecipient"
            @blur="addRecipient"
            placeholder="Add recipient..."
            class="flex-1 min-w-[140px] py-1 bg-transparent border-none text-xs text-ink-gray-9 placeholder:text-ink-gray-4 focus:outline-none"
          />
        </div>

        <!-- CC / BCC Toggles -->
        <div class="flex items-center gap-2 shrink-0">
          <button
            type="button"
            @click="showCC = !showCC"
            class="text-xs transition px-1.5 py-0.5 rounded"
            :class="showCC || ccRecipients.length > 0 ? 'bg-surface-gray-3 text-ink-gray-9 font-medium' : 'text-ink-gray-5 hover:text-ink-gray-8'"
          >
            Cc
          </button>
          <button
            type="button"
            @click="showBCC = !showBCC"
            class="text-xs transition px-1.5 py-0.5 rounded"
            :class="showBCC || bccRecipients.length > 0 ? 'bg-surface-gray-3 text-ink-gray-9 font-medium' : 'text-ink-gray-5 hover:text-ink-gray-8'"
          >
            Bcc
          </button>
        </div>
      </div>

      <!-- CC Row -->
      <div v-if="showCC" class="px-4 py-2 border-t border-outline-gray-1 flex items-center gap-2">
        <span class="text-ink-gray-4 shrink-0 w-8">Cc:</span>
        <div class="flex-1 flex flex-wrap items-center gap-1.5">
          <span
            v-for="email in ccRecipients"
            :key="email"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-surface-gray-2 text-ink-gray-8 text-xs border border-outline-gray-2"
          >
            <span>{{ email }}</span>
            <button type="button" @click="removeCC(email)" class="text-ink-gray-4 hover:text-ink-gray-8">×</button>
          </span>
          <input
            v-model="newCCInput"
            @keydown.enter.prevent="addCC"
            @keydown.comma.prevent="addCC"
            @blur="addCC"
            placeholder="Cc recipients..."
            class="flex-1 min-w-[120px] py-0.5 bg-transparent border-none text-xs text-ink-gray-9 placeholder:text-ink-gray-4 focus:outline-none"
          />
        </div>
      </div>

      <!-- BCC Row -->
      <div v-if="showBCC" class="px-4 py-2 border-t border-outline-gray-1 flex items-center gap-2">
        <span class="text-ink-gray-4 shrink-0 w-8">Bcc:</span>
        <div class="flex-1 flex flex-wrap items-center gap-1.5">
          <span
            v-for="email in bccRecipients"
            :key="email"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-surface-gray-2 text-ink-gray-8 text-xs border border-outline-gray-2"
          >
            <span>{{ email }}</span>
            <button type="button" @click="removeBCC(email)" class="text-ink-gray-4 hover:text-ink-gray-8">×</button>
          </span>
          <input
            v-model="newBCCInput"
            @keydown.enter.prevent="addBCC"
            @keydown.comma.prevent="addBCC"
            @blur="addBCC"
            placeholder="Bcc recipients..."
            class="flex-1 min-w-[120px] py-0.5 bg-transparent border-none text-xs text-ink-gray-9 placeholder:text-ink-gray-4 focus:outline-none"
          />
        </div>
      </div>
    </div>

    <!-- 3. Message Editor Content Area with @ Mention Popover (Screenshots 2 & 3) -->
    <div class="relative !bg-white p-3">
      <div class="rounded-xl border border-outline-gray-2 bg-surface-gray-1/30 hover:bg-surface-gray-1/60 focus-within:bg-white focus-within:border-outline-gray-4 transition shadow-2xs overflow-hidden">
        <textarea
          ref="textareaRef"
          v-model="messageContent"
          :placeholder="activeMode === 'reply' ? 'Type your reply message...' : '@John could you please look into this?'"
          rows="6"
          class="w-full px-4 py-3 text-xs text-ink-gray-9 leading-relaxed bg-transparent border-none focus:outline-none resize-none font-sans"
          @input="handleInput"
          @keydown="handleKeydown"
        ></textarea>

        <!-- Attached Files Chips -->
        <div v-if="attachments.length > 0" class="px-4 pb-2.5 flex flex-wrap gap-2">
          <div
            v-for="(att, idx) in attachments"
            :key="idx"
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-gray-2 text-ink-gray-8 text-xs border border-outline-gray-2"
          >
            <Icon name="tag" size="11" class="text-ink-gray-5" />
            <span class="truncate max-w-[150px]">{{ att.name }}</span>
            <button type="button" @click="removeAttachment(idx)" class="text-ink-gray-4 hover:text-ink-gray-9 font-bold">×</button>
          </div>
        </div>
      </div>

      <!-- @ Mention Floating Menu (Replicated from Screenshot 2) -->
      <div
        v-if="showMentionMenu"
        class="absolute left-6 top-10 z-50 w-60 !bg-white rounded-2xl shadow-xl border border-outline-gray-2 overflow-hidden animate-in fade-in duration-100"
      >
        <div class="px-3.5 py-2 bg-surface-gray-1 border-b border-outline-gray-1 text-[11px] font-semibold text-ink-gray-5">
          Mention team member
        </div>
        <div class="max-h-48 overflow-y-auto p-1.5 space-y-0.5">
          <div
            v-for="(user, uIdx) in mentionUsersList"
            :key="user.name"
            @click="selectMentionUser(user)"
            @mouseenter="mentionActiveIndex = uIdx"
            class="px-2.5 py-1.5 rounded-xl text-xs flex items-center justify-between cursor-pointer transition"
            :class="mentionActiveIndex === uIdx ? 'bg-surface-gray-3 text-ink-gray-9 font-medium' : 'text-ink-gray-7 hover:bg-surface-gray-2'"
          >
            <div class="flex items-center gap-2 min-w-0">
              <Avatar :label="user.full_name || user.name" size="sm" />
              <div class="truncate">
                <div class="font-medium truncate">{{ user.full_name || user.name }}</div>
                <div class="text-[10px] text-ink-gray-4 truncate">{{ user.email || user.name }}</div>
              </div>
            </div>
          </div>
          <div v-if="mentionUsersList.length === 0" class="p-3 text-center text-xs text-ink-gray-4">
            No matching team members
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Bottom Rich Toolbar & Actions (Matching Screenshot 1, 2, 3) -->
    <div class="px-4 py-2 !bg-white border-t border-outline-gray-1 flex items-center justify-between gap-2 overflow-x-auto">
      <!-- Formatting Toolbar -->
      <div class="flex items-center gap-1 text-ink-gray-6 shrink-0">
        <!-- Attachment -->
        <input
          ref="fileInputRef"
          type="file"
          multiple
          class="hidden"
          @change="onFileSelected"
        />
        <button
          type="button"
          @click="$refs.fileInputRef?.click()"
          class="p-1 rounded hover:bg-surface-gray-2 hover:text-ink-gray-9 transition"
          title="Attach files"
        >
          <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
          </svg>
        </button>

        <!-- Quick Canned Replies -->
        <button
          type="button"
          @click="insertCannedReply"
          class="p-1 rounded hover:bg-surface-gray-2 hover:text-ink-gray-9 transition"
          title="Quick Response"
        >
          <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        </button>

        <span class="w-[1px] h-4 bg-outline-gray-2 mx-1"></span>

        <!-- Headings -->
        <button
          type="button"
          @click="insertFormat('\n## ', '')"
          class="px-1.5 py-0.5 text-xs font-semibold rounded hover:bg-surface-gray-2 hover:text-ink-gray-9"
          title="Heading"
        >
          Heading
        </button>
        <button
          type="button"
          @click="insertFormat('\n## ', '')"
          class="px-1 py-0.5 text-[11px] font-semibold rounded hover:bg-surface-gray-2 hover:text-ink-gray-9"
        >
          H2
        </button>
        <button
          type="button"
          @click="insertFormat('\n### ', '')"
          class="px-1 py-0.5 text-[11px] font-semibold rounded hover:bg-surface-gray-2 hover:text-ink-gray-9"
        >
          H3
        </button>
        <button
          type="button"
          @click="insertFormat('\n#### ', '')"
          class="px-1 py-0.5 text-[11px] font-semibold rounded hover:bg-surface-gray-2 hover:text-ink-gray-9"
        >
          H4
        </button>

        <!-- Bold -->
        <button
          type="button"
          @click="wrapFormat('**', '**')"
          class="px-1.5 py-0.5 font-bold rounded hover:bg-surface-gray-2 hover:text-ink-gray-9 text-xs"
          title="Bold"
        >
          B
        </button>

        <!-- Italic -->
        <button
          type="button"
          @click="wrapFormat('*', '*')"
          class="px-1.5 py-0.5 italic rounded hover:bg-surface-gray-2 hover:text-ink-gray-9 text-xs font-serif"
          title="Italic"
        >
          I
        </button>

        <!-- Strikethrough -->
        <button
          type="button"
          @click="wrapFormat('~~', '~~')"
          class="px-1.5 py-0.5 line-through rounded hover:bg-surface-gray-2 hover:text-ink-gray-9 text-xs"
          title="Strikethrough"
        >
          S
        </button>

        <!-- Text style A -->
        <button
          type="button"
          class="px-1.5 py-0.5 rounded hover:bg-surface-gray-2 hover:text-ink-gray-9 text-xs font-medium"
        >
          A
        </button>

        <!-- Link -->
        <button
          type="button"
          @click="insertLink"
          class="p-1 rounded hover:bg-surface-gray-2 hover:text-ink-gray-9"
          title="Insert Link"
        >
          <svg class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
          </svg>
        </button>

        <!-- Alignments -->
        <button type="button" class="p-1 rounded hover:bg-surface-gray-2">
          <svg class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="21" x2="3" y1="6" y2="6"/><line x1="15" x2="3" y1="12" y2="12"/><line x1="17" x2="3" y1="18" y2="18"/>
          </svg>
        </button>
        <button type="button" class="p-1 rounded hover:bg-surface-gray-2">
          <svg class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="21" x2="3" y1="6" y2="6"/><line x1="19" x2="5" y1="12" y2="12"/><line x1="21" x2="3" y1="18" y2="18"/>
          </svg>
        </button>

        <!-- Lists -->
        <button
          type="button"
          @click="insertFormat('\n1. ', '')"
          class="px-1 py-0.5 text-xs font-mono rounded hover:bg-surface-gray-2"
          title="Numbered List"
        >
          :=
        </button>
        <button
          type="button"
          @click="insertFormat('\n- ', '')"
          class="px-1 py-0.5 text-xs font-mono rounded hover:bg-surface-gray-2"
          title="Bullet List"
        >
          :≡
        </button>

        <!-- Quote -->
        <button
          type="button"
          @click="insertFormat('\n> ', '')"
          class="px-1.5 py-0.5 text-xs font-serif font-bold rounded hover:bg-surface-gray-2"
          title="Quote"
        >
          ""
        </button>
      </div>

      <!-- Right Action Buttons -->
      <div class="flex items-center gap-2 shrink-0">
        <Button
          variant="subtle"
          size="sm"
          class="rounded-xl"
          label="Discard"
          @click="handleDiscard"
        />

        <Button
          theme="gray"
          variant="solid"
          size="sm"
          class="rounded-xl"
          :disabled="!hasContent"
          :loading="submitting"
          :label="activeMode === 'reply' ? 'Send (Ctrl + ↵)' : 'Comment (Ctrl + ↵)'"
          @click="handleSubmit"
        />
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { Button, Avatar } from 'frappe-ui'
import EmailIcon from './icons/EmailIcon.vue'
import CommentIcon from './icons/CommentIcon.vue'
import Icon from './Icon.vue'
import { sendTaskEmail, addTaskComment, getUsers } from '../api'

const props = defineProps({
  taskId: {
    type: String,
    required: true,
  },
  clientEmail: {
    type: String,
    default: '',
  },
  clientName: {
    type: String,
    default: '',
  },
  taskSubject: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['submitted'])

const isCollapsed = ref(true)
const activeMode = ref('reply')
const textareaRef = ref(null)
const fileInputRef = ref(null)

function toggleMode(mode) {
  if (isCollapsed.value) {
    isCollapsed.value = false
    activeMode.value = mode
    nextTick(() => {
      textareaRef.value?.focus()
    })
  } else {
    if (activeMode.value === mode) {
      isCollapsed.value = true
    } else {
      activeMode.value = mode
      nextTick(() => {
        textareaRef.value?.focus()
      })
    }
  }
}

function expandReply(recipient = null) {
  isCollapsed.value = false
  activeMode.value = 'reply'
  if (recipient && !toRecipients.value.includes(recipient)) {
    toRecipients.value.push(recipient)
  }
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

function expandComment() {
  isCollapsed.value = false
  activeMode.value = 'comment'
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

defineExpose({
  expandReply,
  expandComment,
  isCollapsed,
})

// Email Recipients
const toRecipients = ref([])
const newRecipientInput = ref('')
const ccRecipients = ref([])
const newCCInput = ref('')
const bccRecipients = ref([])
const newBCCInput = ref('')
const showCC = ref(false)
const showBCC = ref(false)

// Content & Attachments
const messageContent = ref('')
const attachments = ref([])
const submitting = ref(false)

// @ Mentions
const showMentionMenu = ref(false)
const mentionFilter = ref('')
const mentionActiveIndex = ref(0)
const teamUsers = ref([])

const defaultMembers = [
  { name: 'abdullah@beverensoftware.com', full_name: 'Abdullah', email: 'abdullah@beverensoftware.com' },
  { name: 'abid@beverensoftware.com', full_name: 'Abid Khan', email: 'abid@beverensoftware.com' },
  { name: 'balachandar@beverensoftware.com', full_name: 'Balachandar S', email: 'balachandar@beverensoftware.com' },
  { name: 'saiyoni@beverensoftware.com', full_name: 'Saiyoni', email: 'saiyoni@beverensoftware.com' },
  { name: 'shakir@beverensoftware.com', full_name: 'Shakir', email: 'shakir@beverensoftware.com' },
]

onMounted(async () => {
  initRecipients()
  try {
    const list = await getUsers()
    teamUsers.value = list?.length ? list : defaultMembers
  } catch (e) {
    teamUsers.value = defaultMembers
  }
})

watch(() => props.clientEmail, () => {
  initRecipients()
})

function initRecipients() {
  if (props.clientEmail && !toRecipients.value.includes(props.clientEmail)) {
    toRecipients.value = [props.clientEmail]
  }
}

const hasContent = computed(() => {
  return messageContent.value.trim().length > 0
})

const mentionUsersList = computed(() => {
  if (!mentionFilter.value) return teamUsers.value
  const q = mentionFilter.value.toLowerCase()
  return teamUsers.value.filter(u =>
    (u.full_name || '').toLowerCase().includes(q) || (u.name || '').toLowerCase().includes(q)
  )
})

function addRecipient() {
  const val = newRecipientInput.value.trim().replace(',', '')
  if (val && !toRecipients.value.includes(val)) {
    toRecipients.value.push(val)
  }
  newRecipientInput.value = ''
}

function removeRecipient(email) {
  toRecipients.value = toRecipients.value.filter(e => e !== email)
}

function addCC() {
  const val = newCCInput.value.trim().replace(',', '')
  if (val && !ccRecipients.value.includes(val)) {
    ccRecipients.value.push(val)
  }
  newCCInput.value = ''
}

function removeCC(email) {
  ccRecipients.value = ccRecipients.value.filter(e => e !== email)
}

function addBCC() {
  const val = newBCCInput.value.trim().replace(',', '')
  if (val && !bccRecipients.value.includes(val)) {
    bccRecipients.value.push(val)
  }
  newBCCInput.value = ''
}

function removeBCC(email) {
  bccRecipients.value = bccRecipients.value.filter(e => e !== email)
}

// Mention Detection & Keyboard Nav
function handleInput(e) {
  const val = messageContent.value
  const cursorPos = textareaRef.value?.selectionStart || 0
  const textBeforeCursor = val.slice(0, cursorPos)
  const lastAt = textBeforeCursor.lastIndexOf('@')

  if (lastAt !== -1 && (lastAt === 0 || /\s/.test(textBeforeCursor[lastAt - 1]))) {
    const query = textBeforeCursor.slice(lastAt + 1)
    if (!/\s/.test(query)) {
      mentionFilter.value = query
      showMentionMenu.value = true
      mentionActiveIndex.value = 0
      return
    }
  }
  showMentionMenu.value = false
}

function handleKeydown(e) {
  // 1. Ctrl + Enter to submit
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    handleSubmit()
    return
  }

  // 2. Mention menu navigation
  if (showMentionMenu.value) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      mentionActiveIndex.value = (mentionActiveIndex.value + 1) % mentionUsersList.value.length
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      mentionActiveIndex.value = (mentionActiveIndex.value - 1 + mentionUsersList.value.length) % mentionUsersList.value.length
    } else if (e.key === 'Enter') {
      e.preventDefault()
      const u = mentionUsersList.value[mentionActiveIndex.value]
      if (u) selectMentionUser(u)
    } else if (e.key === 'Escape') {
      showMentionMenu.value = false
    }
  }
}

function selectMentionUser(user) {
  const val = messageContent.value
  const cursorPos = textareaRef.value?.selectionStart || 0
  const textBeforeCursor = val.slice(0, cursorPos)
  const lastAt = textBeforeCursor.lastIndexOf('@')

  if (lastAt !== -1) {
    const mentionTag = `@${user.full_name || user.name} `
    messageContent.value = textBeforeCursor.slice(0, lastAt) + mentionTag + val.slice(cursorPos)
  }
  showMentionMenu.value = false
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

// Formatting Toolbar Handlers
function wrapFormat(prefix, suffix) {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = messageContent.value.substring(start, end)
  const replacement = prefix + (selected || 'text') + suffix
  messageContent.value = messageContent.value.substring(0, start) + replacement + messageContent.value.substring(end)
  nextTick(() => {
    el.focus()
    el.setSelectionRange(start + prefix.length, end + prefix.length)
  })
}

function insertFormat(prefix, suffix = '') {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart
  messageContent.value = messageContent.value.substring(0, start) + prefix + suffix + messageContent.value.substring(start)
  nextTick(() => {
    el.focus()
  })
}

function insertLink() {
  const url = prompt('Enter URL:')
  if (url) {
    wrapFormat('[', `](${url})`)
  }
}

function insertCannedReply() {
  const canned = 'Hi,\n\nWe have completed the configuration and verified the setup. Please review and confirm.\n\nBest regards,\nImplementation Team'
  messageContent.value = canned
}

function onFileSelected(e) {
  const files = Array.from(e.target.files || [])
  attachments.value.push(...files)
  e.target.value = ''
}

function removeAttachment(idx) {
  attachments.value.splice(idx, 1)
}

function handleDiscard() {
  messageContent.value = ''
  attachments.value = []
  newRecipientInput.value = ''
  newCCInput.value = ''
  newBCCInput.value = ''
  initRecipients()
  isCollapsed.value = true
}

async function handleSubmit() {
  if (!hasContent.value || submitting.value) return
  submitting.value = true

  try {
    if (activeMode.value === 'reply') {
      const allTo = toRecipients.value.length ? toRecipients.value.join(', ') : props.clientEmail
      await sendTaskEmail(
        props.taskId,
        allTo,
        `Re: [${props.taskId}] ${props.taskSubject}`,
        messageContent.value
      )
    } else {
      await addTaskComment(props.taskId, messageContent.value)
    }

    messageContent.value = ''
    attachments.value = []
    isCollapsed.value = true
    emit('submitted')
  } catch (e) {
    alert('Failed to send: ' + e.message)
  } finally {
    submitting.value = false
  }
}
</script>

