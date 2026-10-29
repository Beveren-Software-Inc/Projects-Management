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
              <p class="text-[11px] text-ink-gray-5 mt-0.5">The sidebar uses the Beveren mark. The line under the company name is always the signed-in user.</p>
            </div>

            <div class="p-4 rounded-2xl border border-outline-gray-2 bg-[#f7f8fb] space-y-3">
              <div class="text-[10px] font-semibold uppercase tracking-wider text-ink-gray-4">Sidebar header</div>
              <img :src="logoLight" alt="Beveren" class="h-10 w-auto rounded-lg" />
              <div class="flex items-center gap-3 p-3 rounded-xl bg-white border border-outline-gray-2 shadow-2xs max-w-xs">
                <div class="size-8 rounded-lg overflow-hidden shrink-0">
                  <BrandLogo />
                </div>
                <div class="truncate">
                  <div class="font-semibold text-xs text-ink-gray-9 truncate">{{ settings.brandName || 'Beveren' }}</div>
                  <div class="text-[11px] text-ink-gray-5 truncate">{{ userName }}</div>
                </div>
              </div>
            </div>

            <!-- Inputs -->
            <div>
              <label class="block text-xs font-medium text-ink-gray-7 mb-1">Brand / Company Name</label>
              <input
                v-model="settings.brandName"
                type="text"
                placeholder="Beveren"
                class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none focus:border-outline-gray-4 transition shadow-2xs"
              />
              <p class="mt-2 text-[11px] text-ink-gray-5">The name under the brand is the person who is signed in: {{ userName }}.</p>
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
import { computed, ref, onMounted } from 'vue'
import { Button, Checkbox } from 'frappe-ui'
import Icon from './Icon.vue'
import BrandLogo from './BrandLogo.vue'
import { sessionUserName } from '@/sessionUser'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'saved'])

const activeTab = ref('branding')
const userName = computed(() => sessionUserName())
const logoLight = '/assets/projects/brand/logo-light.jpg'

const SETTINGS_TABS = [
  { id: 'branding', label: 'Branding & App Icon', icon: 'settings' },
  { id: 'notifications', label: 'Email Notifications', icon: 'mail' },
  { id: 'sla', label: 'Task & SLA Defaults', icon: 'clock' },
]

const settings = ref({
  brandName: 'Beveren',
  brandSubtitle: '',
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

