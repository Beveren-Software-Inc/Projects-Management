<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 select-none"
    @click.self="$emit('close')"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl border border-outline-gray-2 w-full max-w-4xl h-[620px] overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-outline-gray-2 flex items-center justify-between bg-white rounded-t-2xl shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-surface-gray-2 border border-outline-gray-2 flex items-center justify-center text-ink-gray-7">
            <Icon name="settings" size="18" />
          </div>
          <div>
            <h2 class="text-sm font-semibold text-ink-gray-9">Projects App Settings</h2>
            <p class="text-[11px] text-ink-gray-5">Configure branding, app icon, notification preferences, and default SLA targets.</p>
          </div>
        </div>

        <button
          type="button"
          @click="$emit('close')"
          class="p-1.5 text-ink-gray-4 hover:text-ink-gray-7 rounded-xl hover:bg-surface-gray-2 transition cursor-pointer"
        >
          <Icon name="x" size="16" />
        </button>
      </div>

      <!-- Settings Split Layout (Sidebar + Content) -->
      <div class="flex-1 flex overflow-hidden">
        <!-- Settings Sidebar Navigation -->
        <div class="w-56 border-r border-outline-gray-1 bg-surface-gray-1 p-3 space-y-1 shrink-0 overflow-y-auto">
          <button
            type="button"
            v-for="tab in SETTINGS_TABS"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition cursor-pointer text-left"
            :class="activeTab === tab.id
              ? 'bg-white text-ink-gray-9 font-semibold shadow-2xs border border-outline-gray-2'
              : 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-gray-2 border border-transparent'"
          >
            <Icon :name="tab.icon" size="14" :class="activeTab === tab.id ? 'text-ink-gray-9' : 'text-ink-gray-5'" />
            <span class="truncate">{{ tab.label }}</span>
          </button>
        </div>

        <!-- Settings Content Area -->
        <div class="flex-1 overflow-y-auto p-6 bg-white text-xs">
          <!-- TAB 1: BRANDING & APP ICON -->
          <div v-if="activeTab === 'branding'" class="space-y-6">
            <div>
              <h3 class="text-xs font-semibold text-ink-gray-9">App Identity & Logo</h3>
              <p class="text-[11px] text-ink-gray-5 mt-0.5">Customize the workspace brand name, subtitle, and attached icon displayed in the sidebar.</p>
            </div>

            <!-- Live Sidebar Header Preview Card -->
            <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-gray-1 space-y-2">
              <div class="text-[10px] font-semibold uppercase tracking-wider text-ink-gray-4">Live Sidebar Header Preview</div>
              <div class="flex items-center gap-3 p-3 rounded-xl bg-white border border-outline-gray-2 shadow-2xs max-w-xs">
                <!-- Preview Icon -->
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
                  <div class="font-semibold text-xs text-ink-gray-9 truncate">{{ settings.brandName || 'Beveren Software' }}</div>
                  <div class="text-[11px] text-ink-gray-5 truncate">{{ settings.brandSubtitle || 'Abid Khan' }}</div>
                </div>
              </div>
            </div>

            <!-- Inputs -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-ink-gray-7 mb-1">Brand / Company Name</label>
                <input
                  v-model="settings.brandName"
                  type="text"
                  placeholder="e.g. Beveren Software"
                  class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-ink-gray-7 mb-1">Subtitle / User Name</label>
                <input
                  v-model="settings.brandSubtitle"
                  type="text"
                  placeholder="e.g. Abid Khan"
                  class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
                />
              </div>
            </div>

            <!-- Brand Color Theme -->
            <div class="space-y-1.5">
              <label class="block text-xs font-medium text-ink-gray-7">Icon Background Color</label>
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
                  <span v-if="settings.brandColor === c" class="text-white text-[10px] font-bold">✓</span>
                </button>
              </div>
            </div>

            <!-- Brand Icon Selection -->
            <div class="space-y-1.5">
              <label class="block text-xs font-medium text-ink-gray-7">Select App Icon</label>
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

          <!-- TAB 2: EMAIL & NOTIFICATIONS (Using the Frappe UI Checkbox Component) -->
          <div v-else-if="activeTab === 'notifications'" class="space-y-6">
            <div>
              <h3 class="text-xs font-semibold text-ink-gray-9">Email & In-App Notifications</h3>
              <p class="text-[11px] text-ink-gray-5 mt-0.5">Control when and how you receive alerts for tasks, project milestones, and team comments.</p>
            </div>

            <!-- Exact Frappe UI Checkbox Pattern Shared by User -->
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
              <h3 class="text-xs font-semibold text-ink-gray-9">SLA & Working Hours</h3>
              <p class="text-[11px] text-ink-gray-5 mt-0.5">Configure target response times, resolution deadlines, and standard working schedules.</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-ink-gray-7 mb-1">First Response SLA (Hours)</label>
                <input
                  v-model.number="settings.firstResponseHours"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-ink-gray-7 mb-1">Resolution SLA (Hours)</label>
                <input
                  v-model.number="settings.resolutionHours"
                  type="number"
                  min="1"
                  class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-ink-gray-7 mb-1">Default Task Priority</label>
                <select
                  v-model="settings.defaultPriority"
                  class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white text-ink-gray-8 focus:outline-none transition shadow-2xs cursor-pointer"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-ink-gray-7 mb-1">Business Hours Schedule</label>
                <input
                  v-model="settings.businessHours"
                  type="text"
                  placeholder="Mon-Fri, 09:00 - 18:00"
                  class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-3.5 border-t border-outline-gray-2 bg-surface-gray-1 flex items-center justify-between rounded-b-2xl shrink-0">
        <div class="text-[11px] text-ink-gray-5">
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
            label="Save Settings"
            @click="handleSave"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, Checkbox } from 'frappe-ui'
import Icon from './Icon.vue'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'saved'])

const activeTab = ref('branding')

const SETTINGS_TABS = [
  { id: 'branding', label: 'Branding & App Icon', icon: 'settings' },
  { id: 'notifications', label: 'Email Notifications', icon: 'mail' },
  { id: 'sla', label: 'Task & SLA Defaults', icon: 'clock' },
]

const COLOR_OPTIONS = [
  '#0f172a', // Slate Navy (Default)
  '#10B981', // Emerald
  '#3B82F6', // Blue
  '#6366F1', // Indigo
  '#8B5CF6', // Violet
  '#EC4899', // Pink
  '#F59E0B', // Amber
  '#06B6D4', // Cyan
  '#14B8A6', // Teal
  '#F43F5E', // Rose
]

const ICON_OPTIONS = [
  'layers',
  'box',
  'folder-kanban',
  'check-square',
  'Cpu',
  'Server',
  'Shield',
  'Wrench',
  'Zap',
  'Award',
  'Target',
  'Package',
  'Briefcase',
  'CreditCard',
  'ShoppingCart',
  'TrendingUp',
  'Users',
  'ticket',
  'settings',
  'Truck',
]

const settings = ref({
  brandName: 'Beveren Software',
  brandSubtitle: 'Abid Khan',
  brandColor: '#0f172a',
  brandIcon: 'layers',
  emailNotifications: true,
  mentions: true,
  threads: true,
  events: false,
  clientUpdates: true,
  firstResponseHours: 4,
  resolutionHours: 24,
  defaultPriority: 'Medium',
  businessHours: 'Mon-Fri, 09:00 - 18:00',
})

onMounted(() => {
  loadSavedSettings()
})

function loadSavedSettings() {
  try {
    const raw = localStorage.getItem('projects_app_settings')
    if (raw) {
      const parsed = JSON.parse(raw)
      settings.value = { ...settings.value, ...parsed }
    }
  } catch (e) {}
}

function handleSave() {
  try {
    localStorage.setItem('projects_app_settings', JSON.stringify(settings.value))
    emit('saved', settings.value)
    emit('close')
  } catch (e) {
    alert('Failed to save settings: ' + e.message)
  }
}
</script>

