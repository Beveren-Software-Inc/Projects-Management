<template>
  <div class="h-full flex flex-col bg-surface-white overflow-hidden">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center text-sm font-medium text-ink-gray-5 truncate">
          <router-link to="/projects" class="hover:text-ink-gray-8 transition">Projects</router-link>
          <span class="mx-1.5 text-ink-gray-4">/</span>
          <span class="text-ink-gray-9 font-semibold truncate">{{ project.project_name || projectName }}</span>
        </div>
      </template>

      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            variant="subtle"
            size="sm"
            label="Attach Doc"
            @click="showAttachDocModal = true"
          >
            <template #prefix>
              <Icon name="paperclip" size="13" />
            </template>
          </Button>

          <Button
            variant="subtle"
            size="sm"
            label="Send to Customer"
            @click="showEmailModal = true"
          >
            <template #prefix>
              <Icon name="mail" size="13" />
            </template>
          </Button>

          <Button
            variant="subtle"
            size="sm"
            label="Add Module"
            @click="showAddModuleModal = true"
          >
            <template #prefix>
              <Icon name="modules" size="13" />
            </template>
          </Button>

          <Button
            theme="gray"
            variant="solid"
            size="sm"
            label="New Task"
            @click="$emit('open-new-task', project.name)"
          >
            <template #prefix>
              <Icon name="plus" size="13" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="flex items-center gap-2 text-xs text-ink-gray-5">
        <Icon name="refresh" size="16" class="animate-spin text-ink-gray-7" />
        <span>Loading project dashboard...</span>
      </div>
    </div>

    <div v-else-if="!project.name" class="p-12 text-center text-xs text-ink-gray-5">
      Project not found.
    </div>

    <div v-else class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- Frappe UI Alert for client communications status -->
      <Alert
        v-if="project.auto_emails"
        theme="blue"
        title="Automated Client Updates Active"
        description="Kickoff communications and milestone completion updates are delivered automatically to the client point of contact."
      />

      <!-- Project Top Banner Card -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-2 shadow-2xs p-5 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-base font-semibold text-ink-gray-9 flex items-center gap-2.5">
              <span>{{ project.project_name }}</span>
              <!-- Stage Selector -->
              <div class="w-48">
                <Select
                  v-model="project.implementation_stage"
                  @change="handleStageChange"
                  :options="[
                    { label: 'Discovery & Planning', value: 'Discovery' },
                    { label: 'Solution Design', value: 'Design' },
                    { label: 'Configuration', value: 'Configuration & Customization' },
                    { label: 'Data Migration', value: 'Data Migration' },
                    { label: 'UAT & Training', value: 'UAT & Training' },
                    { label: 'Go-Live', value: 'Go-Live' },
                    { label: 'Hypercare', value: 'Hypercare Support' },
                    { label: 'Closed', value: 'Closed' },
                  ]"
                  size="sm"
                />
              </div>
            </h1>
            <div class="text-[11px] text-ink-gray-4 font-mono mt-0.5">#{{ project.name }}</div>
          </div>
        </div>

        <!-- Stakeholders Grid with Frappe UI Avatars -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-outline-gray-2 text-xs">
          <!-- Client PoC -->
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-2 space-y-2">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-surface-blue-2 text-ink-blue-7 flex items-center justify-center shrink-0">
                <Icon name="user" size="11" />
              </div>
              <span>Client Point of Contact</span>
            </div>
            <div class="flex items-center gap-2">
              <Avatar :label="project.client_poc_name || 'Client'" size="sm" />
              <div>
                <div class="font-medium text-ink-gray-9">{{ project.client_poc_name || 'Not assigned' }}</div>
                <div class="text-[11px] text-ink-gray-5">{{ project.client_poc_email || '' }}</div>
              </div>
            </div>
          </div>

          <!-- Partner PoC -->
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-2 space-y-2">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-surface-purple-2 text-ink-purple-7 flex items-center justify-center shrink-0">
                <Icon name="briefcase" size="11" />
              </div>
              <span>Partner Lead / Account</span>
            </div>
            <div class="flex items-center gap-2">
              <Avatar :label="project.partner_poc_name || 'Partner'" size="sm" />
              <div>
                <div class="font-medium text-ink-gray-9">{{ project.partner_poc_name || 'Not assigned' }}</div>
                <div class="text-[11px] text-ink-gray-5">{{ project.partner_poc || '' }}</div>
              </div>
            </div>
          </div>

          <!-- Project Manager -->
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-2 space-y-2">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-surface-green-2 text-ink-green-7 flex items-center justify-center shrink-0">
                <Icon name="target" size="11" />
              </div>
              <span>Project Manager</span>
            </div>
            <div class="flex items-center gap-2">
              <Avatar :label="project.project_manager_name || 'PM'" size="sm" />
              <div>
                <div class="font-medium text-ink-gray-9">{{ project.project_manager_name || 'Not assigned' }}</div>
                <div class="text-[11px] text-ink-gray-5">{{ project.project_manager || '' }}</div>
              </div>
            </div>
          </div>

          <!-- Timeline -->
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-2 space-y-1">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-surface-amber-2 text-ink-amber-7 flex items-center justify-center shrink-0">
                <Icon name="clock" size="11" />
              </div>
              <span>Timeline</span>
            </div>
            <div class="font-medium text-ink-gray-9">
              {{ formatDate(project.expected_start_date) }} - {{ formatDate(project.expected_end_date) }}
            </div>
            <div class="text-[11px] flex items-center gap-1" :class="project.auto_emails ? 'text-ink-green-7' : 'text-ink-gray-4'">
              <span>{{ project.auto_emails ? '✓ Auto-emails enabled' : 'Auto-emails disabled' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats row with Dual Progress calculation -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Completion Rate</span>
            <div class="w-7 h-7 rounded-lg bg-surface-blue-2 text-ink-blue-7 flex items-center justify-center shrink-0">
              <Icon name="trending-up" size="13" />
            </div>
          </div>
          <div class="flex items-baseline justify-between">
            <div class="text-2xl font-bold text-ink-gray-9">{{ project.stats?.percent_complete || 0 }}%</div>
            <Badge
              theme="blue"
              variant="subtle"
              size="sm"
              :label="project.stats?.progress_basis === 'hours' ? 'Hours-based' : 'Task-based'"
            />
          </div>
          <Progress :value="project.stats?.percent_complete || 0" size="sm" />
          <div class="text-[11px] text-ink-gray-4">
            <span v-if="project.stats?.progress_basis === 'hours'">
              {{ project.stats?.completed_estimated_hours || 0 }}h of {{ project.stats?.total_estimated_hours || 0 }}h estimated
            </span>
            <span v-else>
              {{ project.stats?.completed_tasks || 0 }} of {{ project.stats?.total_tasks || 0 }} tasks
            </span>
          </div>
        </div>

        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Total Tasks</span>
            <div class="w-7 h-7 rounded-lg bg-surface-gray-2 text-ink-gray-7 flex items-center justify-center shrink-0">
              <Icon name="check-square" size="13" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ project.stats?.total_tasks || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">{{ project.stats?.completed_tasks || 0 }} completed</div>
        </div>

        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">In Progress</span>
            <div class="w-7 h-7 rounded-lg bg-surface-green-2 text-ink-green-7 flex items-center justify-center shrink-0">
              <Icon name="refresh" size="13" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ project.stats?.open_tasks || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">Active workload</div>
        </div>

        <div
          class="p-4 rounded-2xl border shadow-2xs space-y-1 hover:shadow-xs transition"
          :class="(project.stats?.overdue_tasks || 0) > 0 ? 'border-outline-red-3 bg-surface-red-2/30' : 'border-outline-gray-2 bg-surface-white'"
        >
          <div class="flex items-center justify-between text-xs" :class="(project.stats?.overdue_tasks || 0) > 0 ? 'text-ink-red-7 font-medium' : 'text-ink-gray-5'">
            <span class="font-medium">Overdue Tasks</span>
            <div
              class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
              :class="(project.stats?.overdue_tasks || 0) > 0 ? 'bg-surface-red-2 text-ink-red-7' : 'bg-surface-gray-2 text-ink-gray-6'"
            >
              <Icon name="alert-circle" size="13" />
            </div>
          </div>
          <div class="text-2xl font-bold" :class="(project.stats?.overdue_tasks || 0) > 0 ? 'text-ink-red-7' : 'text-ink-gray-9'">
            {{ project.stats?.overdue_tasks || 0 }}
          </div>
          <div class="text-[11px] text-ink-gray-4">Needs priority action</div>
        </div>

        <div class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white shadow-2xs space-y-1 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Milestones</span>
            <div class="w-7 h-7 rounded-lg bg-surface-amber-2 text-ink-amber-7 flex items-center justify-center shrink-0">
              <Icon name="flag" size="13" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-amber-7">
            {{ project.stats?.completed_milestones || 0 }} <span class="text-ink-gray-4 text-base font-normal">/ {{ project.stats?.milestone_count || 0 }}</span>
          </div>
          <div class="text-[11px] text-ink-gray-4">Signed-off</div>
        </div>
      </div>

      <!-- Modules, Tasks, Files & Activity Tabs -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-2 shadow-2xs overflow-hidden">
        <div class="px-5 py-2 border-b border-outline-gray-2 bg-surface-gray-1">
          <TabButtons
            :buttons="[
              { label: `Modules (${project.modules?.length || 0})`, value: 'modules' },
              { label: `Tasks (${project.tasks?.length || 0})`, value: 'tasks' },
              { label: `Files & Scope Docs (${(project.governance?.documents?.length || 0) + (project.files?.length || 0)})`, value: 'files' },
              { label: `Activity & Emails (${activityList.length})`, value: 'activity' },
            ]"
            v-model="activeTab"
          />
        </div>

        <!-- Tab 1: Modules Grid -->
        <div v-show="activeTab === 'modules'" class="p-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            <div
              v-for="mod in project.modules"
              :key="mod.module"
              class="p-4 rounded-2xl border border-outline-gray-2 bg-surface-white hover:shadow-xs transition space-y-3"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border"
                    :style="{
                      backgroundColor: (mod.color || getModuleColor(mod.module_name)) + '18',
                      borderColor: (mod.color || getModuleColor(mod.module_name)) + '38',
                      color: mod.color || getModuleColor(mod.module_name)
                    }"
                  >
                    <Icon
                      :name="mod.icon || getModuleIcon(mod.module_name)"
                      size="18"
                      :color="mod.color || getModuleColor(mod.module_name)"
                    />
                  </div>
                  <div>
                    <div class="font-semibold text-xs text-ink-gray-9">{{ mod.module_name }}</div>
                    <div class="text-[11px] text-ink-gray-5">{{ mod.completed_tasks || 0 }}/{{ mod.total_tasks || 0 }} tasks done</div>
                  </div>
                </div>
                <Badge
                  theme="gray"
                  variant="subtle"
                  size="sm"
                  :label="(mod.progress || 0) + '%'"
                />
              </div>

              <!-- Progress bar -->
              <Progress :value="mod.progress || 0" size="sm" />

              <div class="flex items-center justify-between text-[11px] text-ink-gray-5 pt-0.5">
                <span>{{ (mod.total_tasks || 0) - (mod.completed_tasks || 0) }} pending tasks</span>
                <span class="text-ink-blue-7 font-medium cursor-pointer" @click="activeTab = 'tasks'">View tasks →</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 2: Tasks Table -->
        <div v-show="activeTab === 'tasks'" class="p-5">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead>
                <tr class="bg-surface-gray-1 text-ink-gray-5 font-medium border-b border-outline-gray-2">
                  <th class="py-2.5 px-3">Subject</th>
                  <th class="py-2.5 px-3">Module</th>
                  <th class="py-2.5 px-3">Status</th>
                  <th class="py-2.5 px-3">Priority</th>
                  <th class="py-2.5 px-3">Assignee</th>
                  <th class="py-2.5 px-3">Due Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1">
                <tr v-if="!project.tasks || project.tasks.length === 0">
                  <td colspan="6" class="py-8 text-center text-ink-gray-4 text-xs">
                    No tasks found in this project.
                  </td>
                </tr>
                <tr
                  v-for="t in project.tasks"
                  :key="t.name"
                  class="hover:bg-surface-gray-1/60 transition cursor-pointer"
                  @click="$emit('select-task', t.name)"
                >
                  <td class="py-2.5 px-3 font-medium text-ink-gray-9">
                    <div class="flex items-center gap-1.5">
                      <span v-if="t.is_milestone" class="text-ink-amber-7 font-bold" title="Key Milestone">★</span>
                      <span>{{ t.subject }}</span>
                    </div>
                  </td>
                  <td class="py-2.5 px-3 text-ink-gray-6">{{ t.module_name || t.implementation_module || '-' }}</td>
                  <td class="py-2.5 px-3">
                    <Badge
                      :theme="t.status === 'Completed' ? 'green' : 'gray'"
                      variant="subtle"
                      size="sm"
                      :label="t.status"
                    />
                  </td>
                  <td class="py-2.5 px-3">
                    <Badge
                      :theme="t.priority === 'High' || t.priority === 'Urgent' ? 'red' : 'gray'"
                      variant="subtle"
                      size="sm"
                      :label="t.priority || 'Medium'"
                    />
                  </td>
                  <td class="py-2.5 px-3 text-ink-gray-6">
                    {{ (t.assignees || []).map(a => a.full_name || a.email).join(', ') || 'Unassigned' }}
                  </td>
                  <td class="py-2.5 px-3 text-ink-gray-6">{{ formatDate(t.exp_end_date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab 3: Governance Docs & Attachments -->
        <div v-show="activeTab === 'files'" class="p-5 space-y-4">
          <div class="flex items-center justify-between pb-2 border-b border-outline-gray-2">
            <div>
              <h3 class="text-xs font-semibold text-ink-gray-9">Scope Documents, MoM & Governance Records</h3>
              <p class="text-[11px] text-ink-gray-5">Official implementation artifacts, discussion notes, and governed links.</p>
            </div>
            <Button
              variant="subtle"
              size="sm"
              label="Attach Document"
              @click="showAttachDocModal = true"
            >
              <template #prefix>
                <Icon name="plus" size="13" />
              </template>
            </Button>
          </div>

          <div v-if="project.governance?.documents?.length" class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              v-for="doc in project.governance.documents"
              :key="doc.id"
              class="p-4 bg-surface-white rounded-xl border border-outline-gray-2 shadow-2xs space-y-2 hover:border-outline-gray-3 transition"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="flex items-start gap-2.5 min-w-0">
                  <div class="w-8 h-8 rounded-lg bg-surface-green-2 text-ink-green-7 flex items-center justify-center shrink-0">
                    <Icon name="file-text" :size="16" />
                  </div>
                  <div class="min-w-0">
                    <div class="font-semibold text-xs text-ink-gray-9 truncate">{{ doc.title }}</div>
                    <div class="text-[11px] text-ink-gray-4 flex items-center gap-1.5 mt-0.5">
                      <Badge theme="gray" variant="subtle" size="sm" :label="doc.category" />
                      <span v-if="doc.version">· {{ doc.version }}</span>
                      <span v-if="doc.access_level">· {{ doc.access_level }}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-1 shrink-0">
                  <a
                    v-if="doc.file_url || doc.url"
                    :href="doc.file_url || doc.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="p-1 text-ink-gray-5 hover:text-ink-blue-7 rounded transition"
                    title="Open Document"
                  >
                    <Icon name="external-link" :size="14" />
                  </a>
                  <button
                    type="button"
                    class="p-1 text-ink-gray-4 hover:text-ink-red-7 rounded transition"
                    title="Delete Document"
                    @click="removeDoc(doc.id)"
                  >
                    <Icon name="trash-2" :size="14" />
                  </button>
                </div>
              </div>

              <p v-if="doc.notes" class="text-[11px] text-ink-gray-6 line-clamp-2">{{ doc.notes }}</p>
              <div class="text-[10px] text-ink-gray-4 flex items-center justify-between pt-1 border-t border-outline-gray-1">
                <span>By {{ doc.owner || doc.attached_by || 'Team' }}</span>
                <span>{{ formatDate(doc.attached_at) }} · {{ formatBytes(doc.file_size) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center text-xs text-ink-gray-4">
            No scope or governance documents attached yet. Click "Attach Document" above to upload scope notes or links.
          </div>
        </div>

        <!-- Tab 4: Activity & Customer Communications Timeline -->
        <div v-show="activeTab === 'activity'" class="p-5 space-y-4">
          <div class="flex items-center justify-between pb-2 border-b border-outline-gray-2">
            <div>
              <h3 class="text-xs font-semibold text-ink-gray-9">360° Project Activity & Customer Communications</h3>
              <p class="text-[11px] text-ink-gray-5">Audit trail of weekly progress summaries, customer feedback, and milestones.</p>
            </div>
            <Button
              variant="subtle"
              size="sm"
              label="Send Update"
              @click="showEmailModal = true"
            >
              <template #prefix>
                <Icon name="mail" size="13" />
              </template>
            </Button>
          </div>

          <div v-if="activityList.length" class="space-y-3">
            <div
              v-for="event in activityList"
              :key="event.id"
              class="p-4 bg-surface-white rounded-xl border border-outline-gray-2 shadow-2xs space-y-2 hover:border-outline-gray-3 transition"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="flex items-center gap-2">
                  <Badge
                    :theme="event.tone === 'blue' ? 'blue' : event.tone === 'amber' ? 'amber' : 'gray'"
                    variant="subtle"
                    size="sm"
                    :label="event.label"
                  />
                  <span class="text-xs font-semibold text-ink-gray-9">{{ event.subject || event.title }}</span>
                </div>
                <div class="text-[11px] text-ink-gray-4 whitespace-nowrap">
                  {{ formatDateTime(event.creation || event.timestamp) }}
                </div>
              </div>

              <p class="text-xs text-ink-gray-7 line-clamp-3 leading-relaxed">
                {{ plainText(event.content || event.description) }}
              </p>

              <div class="flex items-center justify-between pt-1 border-t border-outline-gray-1 text-[11px]">
                <div class="text-ink-gray-5">
                  <span v-if="event.sender">By {{ event.sender }}</span>
                  <span v-if="event.recipients"> · To: {{ event.recipients }}</span>
                </div>
                <Button
                  v-if="event.content && event.is_email"
                  variant="ghost"
                  size="sm"
                  label="View Details"
                  @click="viewEmail(event)"
                />
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center text-xs text-ink-gray-4">
            No activity logged yet. Weekly updates and customer feedback emails will appear here.
          </div>
        </div>
      </div>

      <!-- Add Module Modal using Frappe UI Dialog -->
      <Dialog
        :model-value="showAddModuleModal"
        @update:model-value="showAddModuleModal = false"
        title="Add Module to Project"
        size="md"
      >
        <div class="space-y-3 pt-1">
          <p class="text-xs text-ink-gray-5">Select a module to add. Standard tasks will be instantiated automatically.</p>
          <Select
            v-model="moduleToAdd"
            label="Implementation Module *"
            placeholder="Choose Module..."
            :options="availableModuleOptions"
            size="sm"
          />
        </div>

        <template #actions>
          <div class="flex items-center justify-end gap-2 w-full">
            <Button
              variant="subtle"
              size="sm"
              label="Cancel"
              @click="showAddModuleModal = false"
            />
            <Button
              theme="gray"
              variant="solid"
              size="sm"
              :disabled="!moduleToAdd || addingModule"
              :loading="addingModule"
              label="Add Module & Tasks"
              @click="handleAddModule"
            />
          </div>
        </template>
      </Dialog>

      <!-- View Sent Communication Details Dialog using Frappe UI Dialog -->
      <Dialog
        :model-value="Boolean(selectedEmailView)"
        @update:model-value="selectedEmailView = null"
        :title="selectedEmailView?.subject || 'Customer Communication'"
        size="2xl"
      >
        <div v-if="selectedEmailView" class="space-y-3 pt-1">
          <div class="p-3 bg-surface-gray-1 rounded-xl border border-outline-gray-2 text-xs space-y-1">
            <div><span class="font-medium text-ink-gray-5">Recipients:</span> <span class="text-ink-gray-9 font-mono">{{ selectedEmailView.recipients }}</span></div>
            <div v-if="selectedEmailView.cc"><span class="font-medium text-ink-gray-5">CC:</span> <span class="text-ink-gray-9 font-mono">{{ selectedEmailView.cc }}</span></div>
            <div><span class="font-medium text-ink-gray-5">Sent:</span> <span class="text-ink-gray-7">{{ formatDateTime(selectedEmailView.creation || selectedEmailView.sent_at) }}</span></div>
          </div>

          <div class="p-4 border border-outline-gray-2 rounded-xl bg-surface-white text-xs max-h-[50vh] overflow-y-auto">
            <div v-html="selectedEmailView.content" />
          </div>
        </div>

        <template #actions>
          <div class="flex items-center justify-end w-full">
            <Button
              variant="subtle"
              size="sm"
              label="Close"
              @click="selectedEmailView = null"
            />
          </div>
        </template>
      </Dialog>

      <!-- Project Customer Email Modal -->
      <ProjectEmailModal
        v-if="showEmailModal"
        :project="project"
        :project-name="projectName"
        @close="showEmailModal = false"
        @sent="loadProject"
      />

      <!-- Attach Scope / MoM / Governed Doc Modal -->
      <AttachProjectDocModal
        v-if="showAttachDocModal"
        :project-name="project.name || projectName"
        @close="showAttachDocModal = false"
        @attached="loadProject"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  Dialog,
  Button,
  Badge,
  Avatar,
  Progress,
  Alert,
  Select,
  TabButtons,
  toast,
} from 'frappe-ui'
import Icon from '../components/Icon.vue'
import LayoutHeader from '../components/LayoutHeader.vue'
import ProjectEmailModal from '../components/ProjectEmailModal.vue'
import AttachProjectDocModal from '../components/AttachProjectDocModal.vue'
import {
  getProject,
  updateProject,
  addModuleToProject,
  getImplementationModules,
  deleteProjectGovernanceDoc,
} from '../api'

const props = defineProps({
  projectName: {
    type: String,
    required: true,
  },
})

defineEmits(['open-new-task', 'select-task'])

const loading = ref(true)
const project = ref({})
const activeTab = ref('modules')

const showAddModuleModal = ref(false)
const showEmailModal = ref(false)
const showAttachDocModal = ref(false)
const selectedEmailView = ref(null)

const moduleToAdd = ref('')
const addingModule = ref(false)
const allModules = ref([])

const activityList = computed(() => {
  return project.value.activity || project.value.recent_activities || []
})

const availableModuleOptions = computed(() => {
  return [
    { label: '-- Choose Module --', value: '' },
    ...allModules.value.map(m => {
      const already = project.value.modules?.some(pm => pm.module === m.module_code)
      return {
        label: `${m.module_name} ${already ? '(Already added)' : ''}`,
        value: m.module_code,
        disabled: already,
      }
    }),
  ]
})

onMounted(async () => {
  await loadProject()
  try {
    allModules.value = await getImplementationModules()
  } catch (e) {}
})

watch(() => props.projectName, async () => {
  await loadProject()
})

async function loadProject() {
  loading.value = true
  try {
    project.value = await getProject(props.projectName)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleStageChange() {
  try {
    await updateProject(project.value.name, { implementation_stage: project.value.implementation_stage })
    toast.success('Project stage updated')
  } catch (e) {
    toast.error('Failed to update stage: ' + e.message)
  }
}

async function handleAddModule() {
  if (!moduleToAdd.value) return
  addingModule.value = true
  try {
    await addModuleToProject(project.value.name, moduleToAdd.value)
    showAddModuleModal.value = false
    moduleToAdd.value = ''
    toast.success('Module added successfully with tasks')
    await loadProject()
  } catch (e) {
    toast.error('Error adding module: ' + e.message)
  } finally {
    addingModule.value = false
  }
}

async function removeDoc(docId) {
  if (!confirm('Are you sure you want to remove this governance document?')) return
  try {
    await deleteProjectGovernanceDoc(project.value.name, docId)
    toast.success('Document removed')
    await loadProject()
  } catch (e) {
    toast.error('Failed to remove document: ' + (e.message || e))
  }
}

function viewEmail(event) {
  selectedEmailView.value = event
}

function plainText(content) {
  if (!content) return ''
  return String(content).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

function formatBytes(size) {
  const value = Number(size || 0)
  if (!value) return '0 B'
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`
  return `${(value / (1024 * 1024)).toFixed(1)} MB`
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(String(dateStr).replace(' ', 'T'))
    if (isNaN(d.getTime())) return String(dateStr)
    return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
  } catch (e) {
    return String(dateStr)
  }
}

const MODULE_META = {
  accounts: { color: '#10B981', icon: 'CreditCard' },
  buying: { color: '#F59E0B', icon: 'ShoppingCart' },
  selling: { color: '#3B82F6', icon: 'TrendingUp' },
  stock: { color: '#8B5CF6', icon: 'Package' },
  hrms: { color: '#EC4899', icon: 'Users' },
  crm: { color: '#06B6D4', icon: 'Target' },
  manufacturing: { color: '#6366F1', icon: 'Cpu' },
  support: { color: '#F97316', icon: 'LifeBuoy' },
  assets: { color: '#14B8A6', icon: 'Server' },
}

function getModuleColor(nameOrCode) {
  if (!nameOrCode) return '#3B82F6'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_META)) {
    if (key.includes(k)) return v.color
  }
  return '#3B82F6'
}

function getModuleIcon(nameOrCode) {
  if (!nameOrCode) return 'package'
  const key = String(nameOrCode).toLowerCase()
  for (const [k, v] of Object.entries(MODULE_META)) {
    if (key.includes(k)) return v.icon
  }
  return 'package'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr.split(' ')[0])
    if (isNaN(d.getTime())) return dateStr
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>
