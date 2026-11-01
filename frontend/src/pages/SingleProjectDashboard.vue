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
            theme="blue"
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
      <div class="bg-surface-white rounded-2xl border border-outline-gray-1 shadow-2xs p-5 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-base font-semibold text-ink-gray-9 flex items-center gap-2.5">
              <span>{{ project.project_name }}</span>
              <!-- Stage Selector -->
              <select
                v-model="project.implementation_stage"
                @change="handleStageChange"
                class="px-3 py-1 text-xs font-medium rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 text-ink-gray-8 cursor-pointer focus:outline-none transition shadow-2xs"
              >
                <option value="Discovery">Discovery & Planning</option>
                <option value="Design">Solution Design</option>
                <option value="Configuration & Customization">Configuration</option>
                <option value="Data Migration">Data Migration</option>
                <option value="UAT & Training">UAT & Training</option>
                <option value="Go-Live">Go-Live</option>
                <option value="Hypercare Support">Hypercare</option>
                <option value="Closed">Closed</option>
              </select>
            </h1>
            <div class="text-[11px] text-ink-gray-4 font-mono mt-0.5">#{{ project.name }}</div>
          </div>
        </div>

        <!-- Stakeholders Grid with Frappe UI Avatars -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-outline-gray-1 text-xs">
          <!-- Client PoC -->
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-1 space-y-2">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shrink-0">
                <Icon name="user" size="11" class="text-blue-600" />
              </div>
              <span>Client Point of Contact</span>
            </div>
            <div class="flex items-center gap-2">
              <Avatar :label="project.client_poc_name || 'Client'" size="sm" />
              <div>
                <div class="font-medium text-ink-gray-9">{{ project.client_poc_name || 'Not specified' }}</div>
                <div v-if="project.client_poc_email" class="text-ink-gray-5 text-[11px]">
                  <a :href="'mailto:' + project.client_poc_email" class="text-ink-gray-7 hover:underline truncate">{{ project.client_poc_email }}</a>
                </div>
              </div>
            </div>
          </div>

          <!-- Partner PoC -->
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-1 space-y-2">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-purple-50 text-purple-600 border border-purple-100 flex items-center justify-center shrink-0">
                <Icon name="users" size="11" class="text-purple-600" />
              </div>
              <span>Partner Lead</span>
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
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-1 space-y-2">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-emerald-50 text-emerald-600 border border-emerald-100 flex items-center justify-center shrink-0">
                <Icon name="target" size="11" class="text-emerald-600" />
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
          <div class="p-3 rounded-xl bg-surface-gray-1 border border-outline-gray-1 space-y-1">
            <div class="text-[11px] font-medium text-ink-gray-5 flex items-center gap-1.5">
              <div class="w-5 h-5 rounded-md bg-amber-50 text-amber-600 border border-amber-100 flex items-center justify-center shrink-0">
                <Icon name="clock" size="11" class="text-amber-600" />
              </div>
              <span>Timeline</span>
            </div>
            <div class="font-medium text-ink-gray-9">
              {{ formatDate(project.expected_start_date) }} - {{ formatDate(project.expected_end_date) }}
            </div>
            <div class="text-[11px] flex items-center gap-1" :class="project.auto_emails ? 'text-emerald-600' : 'text-ink-gray-4'">
              <span>{{ project.auto_emails ? '✓ Auto-emails enabled' : 'Auto-emails disabled' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats row with Dual Progress calculation -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1.5 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Completion Rate</span>
            <div class="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center shrink-0">
              <Icon name="trending-up" size="13" class="text-indigo-600" />
            </div>
          </div>
          <div class="flex items-baseline justify-between">
            <div class="text-2xl font-bold text-ink-gray-9">{{ project.stats?.percent_complete || 0 }}%</div>
            <span
              class="text-[10px] font-medium px-1.5 py-0.5 rounded"
              :class="project.stats?.progress_basis === 'hours' ? 'bg-blue-50 text-blue-700' : 'bg-surface-gray-2 text-ink-gray-6'"
            >
              {{ project.stats?.progress_basis === 'hours' ? 'Hours-based' : 'Task-based' }}
            </span>
          </div>
          <div class="w-full h-1.5 bg-surface-gray-2 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-300"
              :style="{ width: (project.stats?.percent_complete || 0) + '%' }"
            ></div>
          </div>
          <div class="text-[11px] text-ink-gray-4">
            <span v-if="project.stats?.progress_basis === 'hours'">
              {{ project.stats?.completed_estimated_hours || 0 }}h of {{ project.stats?.total_estimated_hours || 0 }}h estimated
            </span>
            <span v-else>
              {{ project.stats?.completed_tasks || 0 }} of {{ project.stats?.total_tasks || 0 }} tasks
            </span>
          </div>
        </div>

        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Total Tasks</span>
            <div class="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shrink-0">
              <Icon name="check-square" size="13" class="text-blue-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ project.stats?.total_tasks || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">{{ project.stats?.completed_tasks || 0 }} completed</div>
        </div>

        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">In Progress</span>
            <div class="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-100 flex items-center justify-center shrink-0">
              <Icon name="refresh" size="13" class="text-emerald-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-ink-gray-9">{{ project.stats?.open_tasks || 0 }}</div>
          <div class="text-[11px] text-ink-gray-4">Active workload</div>
        </div>

        <div
          class="p-4 rounded-2xl border shadow-2xs space-y-1 hover:shadow-xs transition"
          :class="(project.stats?.overdue_tasks || 0) > 0 ? 'border-red-200 bg-red-50/20' : 'border-outline-gray-1 bg-surface-white'"
        >
          <div class="flex items-center justify-between text-xs" :class="(project.stats?.overdue_tasks || 0) > 0 ? 'text-red-700 font-medium' : 'text-ink-gray-5'">
            <span class="font-medium">Overdue Tasks</span>
            <div
              class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
              :class="(project.stats?.overdue_tasks || 0) > 0 ? 'bg-red-100 text-red-600 border border-red-200' : 'bg-rose-50 text-rose-500 border border-rose-100'"
            >
              <Icon name="alert-circle" size="13" />
            </div>
          </div>
          <div class="text-2xl font-bold" :class="(project.stats?.overdue_tasks || 0) > 0 ? 'text-red-600' : 'text-ink-gray-9'">
            {{ project.stats?.overdue_tasks || 0 }}
          </div>
          <div class="text-[11px] text-ink-gray-4">Needs priority action</div>
        </div>

        <div class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white shadow-2xs space-y-1 hover:shadow-xs transition">
          <div class="flex items-center justify-between text-xs text-ink-gray-5">
            <span class="font-medium">Milestones</span>
            <div class="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 border border-amber-100 flex items-center justify-center shrink-0">
              <Icon name="flag" size="13" class="text-amber-600" />
            </div>
          </div>
          <div class="text-2xl font-bold text-amber-600">
            {{ project.stats?.completed_milestones || 0 }} <span class="text-ink-gray-4 text-base font-normal">/ {{ project.stats?.milestone_count || 0 }}</span>
          </div>
          <div class="text-[11px] text-ink-gray-4">Signed-off</div>
        </div>
      </div>

      <!-- Modules, Tasks, Files & Activity Tabs -->
      <div class="bg-surface-white rounded-2xl border border-outline-gray-1 shadow-2xs overflow-hidden">
        <div class="flex border-b border-outline-gray-1 px-5 bg-surface-gray-1 overflow-x-auto">
          <button
            @click="activeTab = 'modules'"
            class="py-3 px-4 text-xs font-medium border-b-2 transition flex items-center gap-1.5 shrink-0"
            :class="activeTab === 'modules' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          >
            <Icon name="modules" size="14" />
            <span>Modules ({{ project.modules?.length || 0 }})</span>
          </button>

          <button
            @click="activeTab = 'tasks'"
            class="py-3 px-4 text-xs font-medium border-b-2 transition flex items-center gap-1.5 shrink-0"
            :class="activeTab === 'tasks' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          >
            <Icon name="check-square" size="14" />
            <span>Tasks ({{ project.tasks?.length || 0 }})</span>
          </button>

          <button
            @click="activeTab = 'files'"
            class="py-3 px-4 text-xs font-medium border-b-2 transition flex items-center gap-1.5 shrink-0"
            :class="activeTab === 'files' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          >
            <Icon name="paperclip" size="14" />
            <span>Files & Scope Docs ({{ (project.governance?.documents?.length || 0) + (project.files?.length || 0) }})</span>
          </button>

          <button
            @click="activeTab = 'activity'"
            class="py-3 px-4 text-xs font-medium border-b-2 transition flex items-center gap-1.5 shrink-0"
            :class="activeTab === 'activity' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          >
            <Icon name="activity" size="14" />
            <span>Activity & Emails ({{ (project.activity?.length || project.recent_activities?.length || 0) }})</span>
          </button>
        </div>

        <!-- Tab 1: Modules Grid -->
        <div v-show="activeTab === 'modules'" class="p-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            <div
              v-for="mod in project.modules"
              :key="mod.module"
              class="p-4 rounded-2xl border border-outline-gray-1 bg-surface-white hover:border-outline-gray-2 hover:shadow-xs transition space-y-3"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border transition shadow-2xs"
                    :style="{
                      backgroundColor: (mod.color || getModuleColor(mod.module_title || mod.module)) + '18',
                      borderColor: (mod.color || getModuleColor(mod.module_title || mod.module)) + '38',
                      color: mod.color || getModuleColor(mod.module_title || mod.module)
                    }"
                  >
                    <Icon
                      :name="mod.icon || getModuleIcon(mod.module_title || mod.module)"
                      size="18"
                      :color="mod.color || getModuleColor(mod.module_title || mod.module)"
                    />
                  </div>
                  <div>
                    <h4 class="font-semibold text-xs text-ink-gray-9">{{ mod.module_title || mod.module_name }}</h4>
                    <div class="text-[10px] text-ink-gray-4">{{ mod.module }}</div>
                  </div>
                </div>

                <span
                  class="text-xs font-bold font-mono px-2 py-0.5 rounded-md"
                  :style="{
                    backgroundColor: (mod.color || getModuleColor(mod.module_title || mod.module)) + '15',
                    color: mod.color || getModuleColor(mod.module_title || mod.module)
                  }"
                >
                  {{ mod.progress || 0 }}%
                </span>
              </div>

              <div class="space-y-1">
                <div class="w-full h-1.5 bg-surface-gray-2 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :style="{
                      width: (mod.progress || 0) + '%',
                      backgroundColor: mod.color || getModuleColor(mod.module_title || mod.module)
                    }"
                  ></div>
                </div>
              </div>

              <div class="pt-2 border-t border-outline-gray-1 flex items-center justify-between text-[11px] text-ink-gray-5">
                <span>{{ mod.completed_tasks || 0 }}/{{ mod.total_tasks || 0 }} tasks</span>
                <span
                  v-if="mod.overdue_tasks > 0"
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 text-red-600 border border-red-200"
                >
                  <Icon name="alert-circle" size="10" />
                  <span>{{ mod.overdue_tasks }} overdue</span>
                </span>
                <span v-else class="text-[10px] text-emerald-600 flex items-center gap-1">
                  <Icon name="check-circle" size="11" />
                  <span>On track</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 2: Tasks List -->
        <div v-show="activeTab === 'tasks'" class="divide-y divide-outline-gray-1">
          <div
            v-for="task in project.tasks"
            :key="task.name"
            @click="$router.push('/tasks/' + task.name)"
            class="p-3.5 px-5 flex items-center justify-between hover:bg-surface-gray-2 cursor-pointer transition select-none group text-xs"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <span v-if="task.is_milestone" class="text-amber-500 shrink-0" title="Milestone">
                <Icon name="flag" size="13" />
              </span>
              <span class="font-mono text-[11px] text-ink-gray-4 shrink-0">#{{ task.name?.split('-')?.pop() || task.name }}</span>
              <span class="font-medium text-xs text-ink-gray-9 group-hover:text-ink-black transition truncate max-w-md">
                {{ task.subject }}
              </span>
              <Badge
                v-if="task.module_title"
                theme="gray"
                variant="subtle"
                size="sm"
                :label="task.module_title"
              />
            </div>

            <div class="flex items-center gap-4 shrink-0 text-xs">
              <Badge
                size="sm"
                variant="subtle"
                :theme="task.status === 'Completed' ? 'green' : 'gray'"
                :label="task.status"
              />
              <span class="text-[11px] text-ink-gray-5">
                {{ formatDate(task.exp_end_date) }}
              </span>
              <span class="font-mono text-[11px] text-ink-gray-5">{{ task.progress || 0 }}%</span>
            </div>
          </div>
          <div v-if="!project.tasks?.length" class="p-8 text-center text-xs text-ink-gray-4">
            No tasks found in this project. Click "New Task" to create one.
          </div>
        </div>

        <!-- Tab 3: Files & Governed Scope Documents -->
        <div v-show="activeTab === 'files'" class="p-5 space-y-6">
          <!-- Governed Scope & MoM Section -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-xs font-semibold text-ink-gray-9 uppercase tracking-wider flex items-center gap-1.5">
                  <Icon name="target" size="13" class="text-blue-600" />
                  <span>Governed Scope Documents & Discussion Notes</span>
                </h3>
                <p class="text-[11px] text-ink-gray-5">Official Scope of Work, steering committee MoM, architecture blueprints, and governed Drive links.</p>
              </div>
              <Button
                variant="subtle"
                size="sm"
                label="Attach Scope / MoM"
                @click="showAttachDocModal = true"
              >
                <template #prefix>
                  <Icon name="plus" size="13" />
                </template>
              </Button>
            </div>

            <div v-if="project.governance?.documents?.length" class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div
                v-for="gDoc in project.governance.documents"
                :key="gDoc.id"
                class="p-4 rounded-xl border border-outline-gray-1 bg-surface-white hover:border-outline-gray-2 shadow-2xs transition flex flex-col justify-between space-y-2 text-xs"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="space-y-1">
                    <div class="flex items-center gap-1.5 flex-wrap">
                      <span class="px-2 py-0.5 text-[10px] font-semibold rounded-md bg-blue-50 text-blue-700 border border-blue-200/60">
                        {{ gDoc.category }}
                      </span>
                      <span v-if="gDoc.drive_version" class="px-1.5 py-0.2 text-[10px] font-medium bg-surface-gray-2 text-ink-gray-7 rounded">
                        {{ gDoc.drive_version }}
                      </span>
                      <span v-if="gDoc.access_level" class="px-1.5 py-0.2 text-[10px] font-medium bg-emerald-50 text-emerald-700 rounded">
                        {{ gDoc.access_level }}
                      </span>
                    </div>
                    <h4 class="font-semibold text-ink-gray-9">{{ gDoc.title }}</h4>
                  </div>
                  <button
                    type="button"
                    class="text-ink-gray-4 hover:text-red-600 p-1 rounded transition"
                    title="Delete document"
                    @click="removeDoc(gDoc.id)"
                  >
                    <Icon name="trash" size="13" />
                  </button>
                </div>

                <p v-if="gDoc.notes" class="text-[11px] text-ink-gray-5 line-clamp-2">{{ gDoc.notes }}</p>

                <div class="flex items-center justify-between pt-2 border-t border-outline-gray-1 text-[11px] text-ink-gray-4">
                  <span>Owner: {{ gDoc.drive_owner || gDoc.uploaded_by_name || 'Team' }}</span>
                  <a
                    :href="gDoc.file_url || gDoc.drive_link || gDoc.url"
                    target="_blank"
                    class="font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    <span>{{ gDoc.drive_link || gDoc.url ? 'Open Drive Link' : 'View File' }}</span>
                    <Icon name="arrow-up-right" size="12" />
                  </a>
                </div>
              </div>
            </div>
            <div v-else class="p-6 bg-surface-gray-1 border border-dashed border-outline-gray-2 rounded-xl text-center text-xs text-ink-gray-4">
              No scope documents or meeting notes attached yet. Click "Attach Scope / MoM" above to add official documents.
            </div>
          </div>

          <!-- Standard Task Attachments Section -->
          <div class="space-y-3 pt-4 border-t border-outline-gray-1">
            <h3 class="text-xs font-semibold text-ink-gray-9 uppercase tracking-wider flex items-center gap-1.5">
              <Icon name="paperclip" size="13" class="text-ink-gray-5" />
              <span>Task & Implementation Attachments</span>
            </h3>
            <div v-if="project.files?.length" class="divide-y divide-outline-gray-1 border border-outline-gray-1 rounded-xl overflow-hidden text-xs">
              <div
                v-for="file in project.files"
                :key="file.name"
                class="p-3 px-4 flex items-center justify-between hover:bg-surface-gray-1 transition"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <Icon name="file" size="14" class="text-ink-gray-5 shrink-0" />
                  <a :href="file.file_url" target="_blank" class="font-medium text-ink-gray-9 hover:text-blue-600 truncate">
                    {{ file.file_name }}
                  </a>
                  <span v-if="file.task_subject" class="text-[11px] text-ink-gray-4 truncate">
                    ({{ file.task_subject }})
                  </span>
                </div>
                <div class="flex items-center gap-3 text-[11px] text-ink-gray-5 shrink-0">
                  <span>{{ formatBytes(file.file_size) }}</span>
                  <span>{{ formatDate(file.creation) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="p-4 text-center text-xs text-ink-gray-4">
              No files attached on tasks yet.
            </div>
          </div>
        </div>

        <!-- Tab 4: Activity & Communications Feed -->
        <div v-show="activeTab === 'activity'" class="p-5 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-outline-gray-1">
            <div>
              <h3 class="text-xs font-semibold text-ink-gray-9 uppercase tracking-wider">Project Activity & Communications Feed</h3>
              <p class="text-[11px] text-ink-gray-5">Unified audit trail of weekly updates, customer feedback surveys, kickoff notes, and task comments.</p>
            </div>
            <Button
              theme="blue"
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
              :key="event.name || event.id"
              class="p-4 rounded-xl border border-outline-gray-1 bg-surface-white hover:border-outline-gray-2 shadow-2xs transition text-xs space-y-2"
            >
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex items-center gap-2">
                  <Avatar :label="event.sender_name || event.sender || 'User'" size="xs" />
                  <span class="font-semibold text-ink-gray-9">{{ event.sender_name || event.sender || 'Someone' }}</span>
                  <span
                    v-if="event.badge"
                    class="px-2 py-0.5 text-[10px] font-semibold rounded-md"
                    :class="eventBadgeClass(event.badge_tone)"
                  >
                    {{ event.badge }}
                  </span>
                </div>
                <span class="text-[11px] text-ink-gray-4">
                  {{ formatDateTime(event.creation || event.sent_at) }}
                </span>
              </div>

              <!-- Communication details -->
              <div v-if="event.activity_type === 'Communication'" class="space-y-1 bg-surface-gray-1 p-3 rounded-lg border border-outline-gray-1">
                <div class="font-medium text-ink-gray-9">Subject: {{ event.subject || 'Customer Update' }}</div>
                <div class="text-[11px] text-ink-gray-5 flex items-center gap-2 flex-wrap">
                  <span>To: {{ event.recipients }}</span>
                  <span v-if="event.cc">| CC: {{ event.cc }}</span>
                </div>
                <p class="text-ink-gray-7 line-clamp-2 pt-0.5 text-[11px]">
                  {{ plainText(event.content) }}
                </p>
                <button
                  type="button"
                  class="text-blue-600 hover:text-blue-800 text-[11px] font-medium pt-1 flex items-center gap-1 cursor-pointer"
                  @click="viewEmail(event)"
                >
                  <Icon name="eye" size="12" />
                  <span>View Full Message</span>
                </button>
              </div>

              <!-- Comment details -->
              <div v-else class="text-ink-gray-8">
                <p class="text-[11px]">{{ plainText(event.content) }}</p>
                <div v-if="event.task_name" class="text-[10px] text-ink-gray-4 mt-1">
                  On task: <b>{{ event.task_subject || event.task_name }}</b>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center text-xs text-ink-gray-4">
            No activity logged yet. Weekly updates and customer feedback emails will appear here.
          </div>
        </div>
      </div>

      <!-- Add Module Modal -->
      <div v-if="showAddModuleModal" class="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
        <div class="bg-surface-white rounded-2xl border border-outline-gray-2 p-5 max-w-md w-full space-y-3.5 shadow-2xl">
          <h3 class="text-sm font-semibold text-ink-gray-9">Add Module to {{ project.project_name }}</h3>
          <p class="text-xs text-ink-gray-5">Select a module to add. Standard tasks will be instantiated automatically.</p>
          
          <select
            v-model="moduleToAdd"
            class="w-full px-3 py-2 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white focus:outline-none transition shadow-2xs cursor-pointer"
          >
            <option value="">-- Choose Module --</option>
            <option
              v-for="m in allModules"
              :key="m.module_code"
              :value="m.module_code"
              :disabled="project.modules?.some(pm => pm.module === m.module_code)"
            >
              {{ m.module_name }} {{ project.modules?.some(pm => pm.module === m.module_code) ? '(Already added)' : '' }}
            </option>
          </select>

          <div class="flex justify-end gap-2 pt-2">
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
        </div>
      </div>

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

      <!-- View Sent Communication Details Dialog -->
      <div v-if="selectedEmailView" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
        <div class="relative w-full max-w-2xl bg-surface-white rounded-2xl shadow-2xl border border-outline-gray-2 overflow-hidden flex flex-col max-h-[85vh]">
          <header class="flex items-center justify-between px-5 py-3.5 border-b border-outline-gray-1 bg-surface-gray-1">
            <div>
              <h3 class="text-sm font-semibold text-ink-gray-9">{{ selectedEmailView.subject || 'Customer Communication' }}</h3>
              <p class="text-[11px] text-ink-gray-5">
                Sent by {{ selectedEmailView.sender_name || selectedEmailView.sender }} · {{ formatDateTime(selectedEmailView.creation || selectedEmailView.sent_at) }}
              </p>
            </div>
            <button
              type="button"
              class="p-1.5 text-ink-gray-4 hover:text-ink-gray-9 hover:bg-surface-gray-2 rounded-lg transition"
              @click="selectedEmailView = null"
            >
              <Icon name="x" size="16" />
            </button>
          </header>
          <div class="p-4 bg-surface-gray-1 border-b border-outline-gray-1 text-xs space-y-1">
            <div><span class="font-medium text-ink-gray-5">Recipients:</span> <span class="text-ink-gray-9 font-mono">{{ selectedEmailView.recipients }}</span></div>
            <div v-if="selectedEmailView.cc"><span class="font-medium text-ink-gray-5">CC:</span> <span class="text-ink-gray-9 font-mono">{{ selectedEmailView.cc }}</span></div>
          </div>
          <div class="flex-1 overflow-y-auto p-5 text-xs email-content-view">
            <div v-html="selectedEmailView.content" />
          </div>
          <footer class="flex justify-end p-3 border-t border-outline-gray-1 bg-surface-gray-1">
            <Button size="sm" variant="subtle" label="Close" @click="selectedEmailView = null" />
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
  } catch (e) {
    alert('Failed to update stage: ' + e.message)
  }
}

async function handleAddModule() {
  if (!moduleToAdd.value) return
  addingModule.value = true
  try {
    await addModuleToProject(project.value.name, moduleToAdd.value)
    showAddModuleModal.value = false
    moduleToAdd.value = ''
    await loadProject()
  } catch (e) {
    alert('Error adding module: ' + e.message)
  } finally {
    addingModule.value = false
  }
}

async function removeDoc(docId) {
  if (!confirm('Are you sure you want to remove this governance document?')) return
  try {
    await deleteProjectGovernanceDoc(project.value.name, docId)
    await loadProject()
  } catch (e) {
    alert('Failed to remove document: ' + (e.message || e))
  }
}

function viewEmail(event) {
  selectedEmailView.value = event
}

function eventBadgeClass(tone) {
  const map = {
    blue: 'bg-blue-50 text-blue-700 border border-blue-200/70',
    amber: 'bg-amber-50 text-amber-700 border border-amber-200/70',
    teal: 'bg-teal-50 text-teal-700 border border-teal-200/70',
    purple: 'bg-purple-50 text-purple-700 border border-purple-200/70',
    coral: 'bg-red-50 text-red-700 border border-red-200/70',
    slate: 'bg-surface-gray-2 text-ink-gray-7 border border-outline-gray-2',
    gray: 'bg-surface-gray-2 text-ink-gray-6 border border-outline-gray-1',
  }
  return map[tone] || 'bg-surface-gray-2 text-ink-gray-7'
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
