<template>
  <Dialog
    :model-value="show"
    @update:model-value="$emit('close')"
    title="Projects App Settings"
    size="4xl"
  >
    <template #title>
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-surface-gray-2 border border-outline-gray-2 flex items-center justify-center text-ink-gray-7">
          <Icon name="settings" size="18" />
        </div>
        <div>
          <h2 class="text-sm font-semibold text-ink-gray-9">Projects App Settings</h2>
          <p class="text-xs text-ink-gray-5">Configure branding, app icon, notification preferences, and default SLA targets.</p>
        </div>
      </div>
    </template>

    <!-- Settings Split Layout (Sidebar + Content) -->
    <div class="flex overflow-hidden h-[480px] -mx-4 -my-4 sm:-mx-6">
      <!-- Settings Sidebar Navigation -->
      <div class="w-56 border-r border-outline-gray-2 bg-surface-gray-1 p-3 space-y-1 shrink-0 overflow-y-auto">
        <button
          type="button"
          v-for="tab in SETTINGS_TABS"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition cursor-pointer text-left"
          :class="activeTab === tab.id
            ? 'bg-white text-ink-gray-9 font-semibold shadow-2xs border border-outline-gray-2'
            : 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-gray-2 border border-transparent'"
        >
          <Icon :name="tab.icon" size="14" :class="activeTab === tab.id ? 'text-ink-gray-9' : 'text-ink-gray-5'" />
          <span class="truncate">{{ tab.label }}</span>
        </button>
      </div>

      <!-- Settings Content Area -->
      <div class="flex-1 overflow-y-auto p-6 bg-surface-white text-sm">
        <!-- TAB 1: BRANDING & APP ICON -->
        <div v-if="activeTab === 'branding'" class="space-y-6">
          <div>
            <h3 class="text-sm font-semibold text-ink-gray-9">App Identity & Logo</h3>
            <p class="text-xs text-ink-gray-5 mt-0.5">Customize the workspace brand name, subtitle, and attached icon displayed in the sidebar.</p>
          </div>

          <!-- Live Sidebar Header Preview Card -->
          <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-gray-1 space-y-2">
            <div class="text-xs font-semibold uppercase tracking-wider text-ink-gray-4">Live Sidebar Header Preview</div>
            <div class="flex items-center gap-3 p-3 rounded-xl bg-white border border-outline-gray-2 shadow-2xs max-w-xs">
              <div
                class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-xs border transition"
                :style="{
                  backgroundColor: settings.brandColor,
                  borderColor: settings.brandColor
                }"
              >
                <Icon :name="settings.brandIcon" size="20" color="#ffffff" />
              </div>
              <div class="truncate">
                <div class="font-semibold text-sm text-ink-gray-9 truncate">{{ companyName }}</div>
                <div class="text-xs text-ink-gray-5 truncate">{{ currentUserName }}</div>
              </div>
            </div>
          </div>

          <!-- Inputs -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="block text-sm font-medium text-ink-gray-7">Brand / Company Name</label>
              <div class="px-2.5 py-1.5 rounded-xl bg-surface-gray-2 text-ink-gray-8 text-sm truncate">{{ companyName }}</div>
            </div>
            <div class="text-xs text-ink-gray-5 self-end pb-1.5">
              The name comes from your default Company, and the subtitle shows the logged-in user.
            </div>
          </div>

          <!-- Brand Color Theme -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-ink-gray-7">Icon Background Color</label>
            <div class="flex flex-wrap items-center gap-2">
              <button
                v-for="c in COLOR_OPTIONS"
                :key="c"
                type="button"
                @click="settings.brandColor = c"
                class="w-6 h-6 rounded-full transition-all flex items-center justify-center cursor-pointer border"
                :style="{
                  backgroundColor: c,
                  borderColor: settings.brandColor === c ? '#1E293B' : 'transparent',
                  transform: settings.brandColor === c ? 'scale(1.15)' : 'scale(1)'
                }"
                :title="c"
              >
                <span v-if="settings.brandColor === c" class="text-white text-xs font-bold">✓</span>
              </button>
            </div>
          </div>

          <!-- Brand Icon Selection -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-ink-gray-7">Select App Icon</label>
            <div class="grid grid-cols-10 gap-2 p-3 bg-surface-gray-1 rounded-xl border border-outline-gray-2 max-h-40 overflow-y-auto">
              <button
                v-for="iconItem in ICON_OPTIONS"
                :key="iconItem"
                type="button"
                @click="settings.brandIcon = iconItem"
                class="p-2 rounded-xl flex items-center justify-center transition cursor-pointer"
                :class="settings.brandIcon === iconItem
                  ? 'bg-white shadow-2xs border border-outline-gray-4 text-ink-gray-9 scale-105'
                  : 'text-ink-gray-5 hover:text-ink-gray-9 hover:bg-surface-gray-2'"
                :title="iconItem"
              >
                <Icon :name="iconItem" size="18" />
              </button>
            </div>
          </div>
        </div>

        <!-- TAB 2: EMAIL & NOTIFICATIONS -->
        <div v-else-if="activeTab === 'notifications'" class="space-y-6">
          <div>
            <h3 class="text-sm font-semibold text-ink-gray-9">Email & In-App Notifications</h3>
            <p class="text-xs text-ink-gray-5 mt-0.5">Control when and how you receive alerts for tasks, project milestones, and team comments.</p>
          </div>

          <div class="p-5 rounded-2xl border border-outline-gray-2 bg-surface-gray-1/60 space-y-4 max-w-xl">
            <Checkbox
              v-model="settings.emailNotifications"
              label="Enable email notifications"
              description="Receive system and task digests to your registered email address."
            />
            <Checkbox
              v-model="settings.mentions"
              label="Mentions"
              description="Notify me whenever someone tags @my_name in a task comment or reply."
            />
            <Checkbox
              v-model="settings.threads"
              label="Email threads on assigned document"
              description="Get notified when an email is received on any of the documents assigned to you."
            />
            <Checkbox
              v-model="settings.events"
              label="Event reminders"
              description="Receive reminder alerts 1 hour before scheduled implementation checkpoints."
            />
            <Checkbox
              v-model="settings.clientUpdates"
              label="Automated Client Updates"
              description="Send automated kickoff communications and milestone status updates to Client PoC."
            />
          </div>
        </div>

        <!-- TAB 3: SLA & WORKFLOW DEFAULTS -->
        <div v-else-if="activeTab === 'sla'" class="space-y-6">
          <div>
            <h3 class="text-sm font-semibold text-ink-gray-9">SLA & Working Hours</h3>
            <p class="text-xs text-ink-gray-5 mt-0.5">Configure target response times, resolution deadlines, and standard working schedules.</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <TextInput
              v-model.number="settings.firstResponseHours"
              type="number"
              label="First Response SLA (Hours)"
              min="1"
              size="sm"
            />
            <TextInput
              v-model.number="settings.resolutionHours"
              type="number"
              label="Resolution SLA (Hours)"
              min="1"
              size="sm"
            />
            <Select
              v-model="settings.defaultPriority"
              label="Default Task Priority"
              :options="[
                { label: 'Low', value: 'Low' },
                { label: 'Medium', value: 'Medium' },
                { label: 'High', value: 'High' },
                { label: 'Urgent', value: 'Urgent' },
              ]"
              size="sm"
            />
            <TextInput
              v-model="settings.businessHours"
              label="Business Hours Schedule"
              placeholder="Mon-Fri, 09:00 - 18:00"
              size="sm"
            />
          </div>
        </div>
      </div>
    </div>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div class="text-xs text-ink-gray-5">
          Changes take effect immediately across all project workspaces.
        </div>
        <div class="flex items-center gap-2">
          <Button
            variant="subtle"
            size="sm"
            label="Cancel"
            @click="$emit('close')"
          />
          <Button
            theme="gray"
            variant="solid"
            size="sm"
            label="Save Preferences"
            @click="saveSettings"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  Dialog,
  Button,
  Checkbox,
  TextInput,
  Select,
  toast,
} from 'frappe-ui'
import Icon from './Icon.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'updated'])

const SETTINGS_KEY = 'beveren_projects_app_settings'

const SETTINGS_TABS = [
  { id: 'branding', label: 'Branding & App Icon', icon: 'palette' },
  { id: 'notifications', label: 'Notifications & Email', icon: 'bell' },
  { id: 'sla', label: 'SLA & Timelines', icon: 'clock' },
]

const COLOR_OPTIONS = [
  '#DC2626', // Red (Beveren)
  '#2563EB', // Blue
  '#059669', // Emerald
  '#7C3AED', // Purple
  '#D97706', // Amber
  '#0891B2', // Cyan
  '#4F46E5', // Indigo
  '#0F172A', // Slate Dark
  '#EA580C', // Orange
  '#E11D48', // Rose
]

const ICON_OPTIONS = [
  'check-square',
  'folder-kanban',
  'package',
  'cpu',
  'trending-up',
  'users',
  'target',
  'briefcase',
  'shield',
  'layers',
  'award',
  'server',
  'activity',
  'zap',
  'settings',
  'database',
  'layout',
  'compass',
  'grid',
  'star',
]

const activeTab = ref('branding')

const defaultSettings = {
  brandColor: '#DC2626',
  brandIcon: 'check-square',
  emailNotifications: true,
  mentions: true,
  threads: true,
  events: true,
  clientUpdates: true,
  firstResponseHours: 4,
  resolutionHours: 24,
  defaultPriority: 'Medium',
  businessHours: 'Mon - Fri (09:00 - 18:00)',
}

const settings = reactive({ ...defaultSettings })

// Company name and logged-in user's name, provided by the page boot (projects/www/projects.py -> user_info)
const companyName = window.company_name || 'Projects'
const currentUserName =
  window.user_info?.full_name ||
  window.user_info?.email ||
  window.session_user ||
  ''

onMounted(() => {
  loadSettings()
})

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      // Drop the old hardcoded per-user subtitle that earlier versions saved
      delete parsed.brandSubtitle
      delete parsed.brandName
      Object.assign(settings, parsed)
    }
  } catch (e) {
    console.error('Failed to load settings from localStorage', e)
  }
}

function saveSettings() {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
    window.dispatchEvent(new CustomEvent('beveren-settings-changed', { detail: { ...settings } }))
    toast.success('App settings saved successfully!')
    emit('updated', { ...settings })
    emit('close')
  } catch (e) {
    toast.error('Failed to save settings: ' + (e.message || e))
  }
}
</script>
