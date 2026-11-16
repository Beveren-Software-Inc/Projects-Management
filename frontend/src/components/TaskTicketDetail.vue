<template>
  <div class="h-full flex flex-col bg-surface-white overflow-hidden select-none">
    <!-- 1. Layout Header (Matching Frappe Helpdesk TicketHeader) -->
    <div class="h-11 px-5 border-b border-outline-gray-1 flex items-center justify-between shrink-0 bg-surface-white">
      <!-- Left Breadcrumbs -->
      <div class="flex items-center gap-1.5 min-w-0 flex-1 text-lg">
        <Button
          v-if="showBack"
          variant="ghost"
          size="sm"
          class="!p-1 text-ink-gray-5 hover:text-ink-gray-8 -ms-1"
          @click="$emit('back')"
          title="Back to Tasks"
        >
          <template #prefix>
            <Icon name="arrow-left" size="14" />
          </template>
        </Button>
        <router-link to="/tasks" class="text-ink-gray-5 hover:text-ink-gray-8 transition font-medium">
          Tasks
        </router-link>
        <span class="text-ink-gray-4">/</span>
        <span class="font-semibold text-ink-gray-9 truncate max-w-xl">
          {{ task.subject || task.name }}
        </span>
      </div>

      <!-- Right Header Actions (Frappe UI Status Dropdown + More Options) -->
      <div class="flex items-center gap-2 shrink-0">
        <!-- Status Pill Dropdown -->
        <Dropdown :options="statusOptions" align="end">
          <template #default="{ open }">
            <Button
              size="sm"
              variant="subtle"
              class="rounded-full shadow-2xs font-medium"
            >
              <template #prefix>
                <IndicatorIcon :class="statusDotClass(task.status)" />
              </template>
              <span>{{ task.status || 'Open' }}</span>
              <template #suffix>
                <Icon name="chevron-down" size="12" class="text-ink-gray-4 transition-transform" :class="{ 'rotate-180': open }" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <!-- More actions dropdown -->
        <Dropdown :options="moreOptions" align="end">
          <template #default>
            <Button
              variant="ghost"
              size="sm"
              class="!p-1.5 text-ink-gray-5 hover:text-ink-gray-8"
              title="More options"
            >
              <template #prefix>
                <Icon name="more-horizontal" size="15" />
              </template>
            </Button>
          </template>
        </Dropdown>

        <Button
          v-if="showClose"
          variant="ghost"
          size="sm"
          class="!p-1 text-ink-gray-4 hover:text-ink-gray-7 ml-1"
          @click="$emit('close')"
        >
          <template #prefix>
            <Icon name="x" size="15" />
          </template>
        </Button>
      </div>
    </div>

    <!-- 2. Sub-Tabs Bar (✦ Activity, ✉ Emails, 💬 Comments, 📊 Analytics) -->
    <div class="flex items-center border-b border-outline-gray-1 px-5 bg-surface-white shrink-0">
      <div class="flex gap-4">
        <button
          @click="activeTab = 'activity'"
          class="flex items-center gap-1.5 py-2.5 text-sm font-medium border-b-2 transition cursor-pointer"
          :class="activeTab === 'activity' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          <ActivityIcon class="size-3.5" :class="activeTab === 'activity' ? 'text-ink-gray-9' : 'text-ink-gray-5'" />
          <span>Activity</span>
        </button>

        <button
          @click="activeTab = 'emails'"
          class="flex items-center gap-1.5 py-2.5 text-sm font-medium border-b-2 transition cursor-pointer"
          :class="activeTab === 'emails' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          <EmailIcon class="size-3.5" :class="activeTab === 'emails' ? 'text-ink-gray-9' : 'text-ink-gray-5'" />
          <span>Emails</span>
          <span
            v-if="emailCount > 0"
            class="text-xs px-1.5 py-0.5 rounded-full font-medium"
            :class="activeTab === 'emails' ? 'bg-surface-gray-3 text-ink-gray-9' : 'bg-surface-gray-2 text-ink-gray-6'"
          >
            {{ emailCount }}
          </span>
        </button>

        <button
          @click="activeTab = 'comments'"
          class="flex items-center gap-1.5 py-2.5 text-sm font-medium border-b-2 transition cursor-pointer"
          :class="activeTab === 'comments' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          <CommentIcon class="size-3.5" :class="activeTab === 'comments' ? 'text-ink-gray-9' : 'text-ink-gray-5'" />
          <span>Comments</span>
          <span
            v-if="commentCount > 0"
            class="text-xs px-1.5 py-0.5 rounded-full font-medium"
            :class="activeTab === 'comments' ? 'bg-surface-gray-3 text-ink-gray-9' : 'bg-surface-gray-2 text-ink-gray-6'"
          >
            {{ commentCount }}
          </span>
        </button>

        <button
          @click="activeTab = 'analytics'"
          class="flex items-center gap-1.5 py-2.5 text-sm font-medium border-b-2 transition cursor-pointer"
          :class="activeTab === 'analytics' ? 'border-ink-gray-9 text-ink-gray-9 font-semibold' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        >
          <Icon name="chart-no-axes-column" size="14" :class="activeTab === 'analytics' ? 'text-ink-gray-9' : 'text-ink-gray-5'" />
          <span>Analytics</span>
        </button>
      </div>
    </div>

    <!-- 3. Ticket Split Content (Left Feed & Right Sidebar) -->
    <div class="flex-1 flex overflow-hidden">
      
      <!-- MAIN FEED COLUMN (Helpdesk TicketAgentActivities + pinned communication area) -->
      <div class="flex-1 flex flex-col overflow-hidden bg-surface-white min-w-0">
        <!-- Tab title row -->
        <div class="flex items-center justify-between gap-2 px-5 sm:px-10 pt-4 pb-3 shrink-0">
          <div class="flex items-center gap-2 min-w-0">
            <h2 class="text-lg font-semibold text-ink-gray-9 truncate">{{ tabTitle }}</h2>
            <Badge
              v-if="task.is_milestone"
              theme="orange"
              variant="subtle"
              size="sm"
              label="Key Milestone"
            />
          </div>
          <Dropdown v-if="activeTab === 'activity'" :options="newActivityOptions" align="end">
            <template #default="{ open }">
              <Button variant="subtle" size="sm" label="New">
                <template #prefix>
                  <Icon name="plus" size="14" />
                </template>
                <template #suffix>
                  <Icon name="chevron-down" size="12" class="transition-transform" :class="{ 'rotate-180': open }" />
                </template>
              </Button>
            </template>
          </Dropdown>
          <Button
            v-else-if="activeTab === 'emails'"
            variant="subtle"
            size="sm"
            label="New Email"
            @click="commAreaRef?.expandReply(task.client_poc_email)"
          >
            <template #prefix>
              <Icon name="plus" size="14" />
            </template>
          </Button>
          <Button
            v-else-if="activeTab === 'comments'"
            variant="subtle"
            size="sm"
            label="New Comment"
            @click="commAreaRef?.expandComment()"
          >
            <template #prefix>
              <Icon name="plus" size="14" />
            </template>
          </Button>
        </div>

        <!-- Scrollable feed -->
        <div ref="feedRef" class="flex-1 overflow-y-auto">
          <div v-if="activeTab !== 'analytics'" class="flex min-h-full flex-col px-5 sm:px-10 pb-4">
            <Alert
              v-if="task.is_overdue && activeTab === 'activity'"
              class="mb-4"
              theme="red"
              title="Task Deadline Overdue"
              :description="'This implementation task was scheduled for completion by ' + formatDate(task.exp_end_date) + '.'"
            />
            <TaskActivities
              :activities="currentActivities"
              :empty-text="emptyState.text"
              :empty-icon="emptyState.icon"
              @reply="onReplyToEmail"
              @comment-updated="onCommentUpdated"
              @comment-deleted="onCommentDeleted"
            />
          </div>

          <!-- ANALYTICS -->
          <div v-else class="px-5 sm:px-10 pb-6">
            <div class="space-y-6">
              <!-- KPI Metric Cards Grid -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3.5">
                <div class="bg-surface-white rounded-2xl border border-outline-gray-1 p-4 shadow-2xs">
                  <div class="text-xs font-medium text-ink-gray-5">Target Response</div>
                  <div class="text-base font-bold text-emerald-600 mt-1">1h 38m</div>
                  <div class="text-xs text-emerald-700 mt-0.5">✓ Target fulfilled</div>
                </div>

                <div class="bg-surface-white rounded-2xl border border-outline-gray-1 p-4 shadow-2xs">
                  <div class="text-xs font-medium text-ink-gray-5">Delivery Target</div>
                  <div class="text-base font-bold text-blue-600 mt-1">{{ task.status === 'Completed' ? 'Delivered' : 'On Schedule' }}</div>
                  <div class="text-xs text-ink-gray-4 mt-0.5">Active milestone track</div>
                </div>

                <div class="bg-surface-white rounded-2xl border border-outline-gray-1 p-4 shadow-2xs">
                  <div class="text-xs font-medium text-ink-gray-5">Total Emails</div>
                  <div class="text-base font-bold text-ink-gray-9 mt-1">{{ emailCount }}</div>
                  <div class="text-xs text-ink-gray-4 mt-0.5">Client communications</div>
                </div>

                <div class="bg-surface-white rounded-2xl border border-outline-gray-1 p-4 shadow-2xs">
                  <div class="text-xs font-medium text-ink-gray-5">Internal Notes</div>
                  <div class="text-base font-bold text-amber-600 mt-1">{{ commentCount }}</div>
                  <div class="text-xs text-ink-gray-4 mt-0.5">Team collaboration logs</div>
                </div>
              </div>

              <!-- Lifecycle Details Card -->
              <div class="bg-surface-white rounded-2xl border border-outline-gray-1 p-5 shadow-2xs space-y-4">
                <h3 class="text-sm font-semibold text-ink-gray-9">Task Lifecycle & Milestone Schedule</h3>
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div class="space-y-2">
                    <div class="flex justify-between py-1 border-b border-outline-gray-1">
                      <span class="text-ink-gray-5">Created By</span>
                      <span class="font-medium text-ink-gray-8">{{ task.owner || 'Administrator' }}</span>
                    </div>
                    <div class="flex justify-between py-1 border-b border-outline-gray-1">
                      <span class="text-ink-gray-5">Creation Date</span>
                      <span class="font-medium text-ink-gray-8">{{ formatDate(task.creation) }}</span>
                    </div>
                    <div class="flex justify-between py-1 border-b border-outline-gray-1">
                      <span class="text-ink-gray-5">Assigned To</span>
                      <span class="font-medium text-ink-gray-8">{{ (task.assignees || []).map(a => a.full_name || a.email).join(', ') || 'Unassigned' }}</span>
                    </div>
                  </div>
                  <div class="space-y-2">
                    <div class="flex justify-between py-1 border-b border-outline-gray-1">
                      <span class="text-ink-gray-5">Expected Start</span>
                      <span class="font-medium text-ink-gray-8">{{ cleanDate(task.exp_start_date) || 'Not set' }}</span>
                    </div>
                    <div class="flex justify-between py-1 border-b border-outline-gray-1">
                      <span class="text-ink-gray-5">Due Date</span>
                      <span class="font-medium text-ink-gray-8">{{ cleanDate(task.exp_end_date) || 'Not set' }}</span>
                    </div>
                    <div class="flex justify-between py-1 border-b border-outline-gray-1">
                      <span class="text-ink-gray-5">Current Status</span>
                      <span class="font-medium text-ink-gray-8">{{ task.status }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- SLA Service Commitment Details -->
              <div class="bg-surface-white rounded-2xl border border-outline-gray-1 p-5 shadow-2xs space-y-3">
                <h3 class="text-sm font-semibold text-ink-gray-9">SLA Service Level Agreement</h3>
                <div class="space-y-2 text-sm text-ink-gray-7">
                  <div class="flex items-center justify-between p-2.5 rounded-xl bg-surface-gray-2">
                    <span class="font-medium">Response Target (4h)</span>
                    <span class="text-emerald-600 font-semibold">Fulfilled in 1h 38m</span>
                  </div>
                  <div class="flex items-center justify-between p-2.5 rounded-xl bg-surface-gray-2">
                    <span class="font-medium">Resolution Target (24h)</span>
                    <span class="text-blue-600 font-semibold">Clock Paused (On Hold)</span>
                  </div>
                  <div class="flex items-center justify-between p-2.5 rounded-xl bg-surface-gray-2">
                    <span class="font-medium">Business Schedule</span>
                    <span class="text-ink-gray-6">Standard Hours (Mon - Fri 09:00 - 18:00)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pinned communication area (Helpdesk TicketAgent bottom bar) -->
        <div
          v-if="activeTab !== 'analytics'"
          class="shrink-0 max-h-[60vh] overflow-y-auto border-t border-outline-gray-1 px-5 sm:px-10 py-3"
        >
          <CommunicationArea
            ref="commAreaRef"
            :task-id="task.name || taskId"
            :client-email="task.client_poc_email || ''"
            :client-name="task.client_poc_name || ''"
            :task-subject="task.subject || ''"
            @submitted="onCommunicationSubmitted"
          />
        </div>
      </div>

      <!-- 4. RIGHT SIDEBAR (Replicated from Helpdesk TicketDetailsTab.vue) -->
      <div class="w-80 bg-surface-white border-l border-outline-gray-1 flex flex-col h-full overflow-hidden shrink-0">
        <!-- Pinned Header: TicketContact + TicketSLA -->
        <div class="shrink-0 p-4 space-y-3.5 border-b border-outline-gray-1">
          <!-- TicketContact (matching Helpdesk TicketContact.vue) -->
          <div class="flex items-center gap-3">
            <Avatar :label="task.client_poc_name || 'Client'" size="3xl" />
            <div class="flex min-w-0 flex-1 flex-col gap-1">
              <p class="truncate text-sm font-medium text-ink-gray-8">
                {{ task.client_poc_name || 'Client Point of Contact' }}
              </p>
              <div class="flex items-center gap-1.5 text-sm text-ink-gray-5">
                <span class="font-mono">#{{ task.name?.split('-')?.pop() || '0202' }}</span>
                <span>•</span>
                <span>via Portal</span>
              </div>
            </div>
          </div>

          <!-- TaskSLA / Delivery Target -->
          <div class="space-y-1.5 text-sm pt-1">
            <!-- Target Response -->
            <div class="flex items-center justify-between">
              <span class="w-[106px] shrink-0 text-ink-gray-5">Target Response</span>
              <div class="flex min-w-0 flex-1 items-center gap-1 ps-2">
                <span class="text-emerald-600 font-medium truncate">Fulfilled in 1h 38m</span>
                <span class="text-ink-gray-4 text-xs cursor-pointer" title="Response Target Met">ⓘ</span>
              </div>
            </div>

            <!-- Delivery Status -->
            <div class="flex items-center justify-between">
              <span class="w-[106px] shrink-0 text-ink-gray-5">Delivery Status</span>
              <div class="flex min-w-0 flex-1 items-center gap-1 ps-2">
                <span
                  class="font-medium truncate"
                  :class="task.status === 'Completed' ? 'text-emerald-600' : task.is_overdue ? 'text-red-600' : 'text-blue-600'"
                >
                  {{ task.status === 'Completed' ? 'Delivered' : task.is_overdue ? 'Overdue Deadline' : 'On Schedule' }}
                </span>
                <span class="text-ink-gray-4 text-xs cursor-pointer" title="Delivery Status">ⓘ</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Scrollable Sections with divide-y (Matching Helpdesk Section.vue) -->
        <div class="flex-1 overflow-y-auto divide-y divide-outline-gray-1">
          <!-- Section 1: Overview (Fully Interactive matching Helpdesk TicketDetailsTab) -->
          <div class="p-4 space-y-3">
            <div
              class="flex items-center justify-between cursor-pointer select-none"
              @click="overviewOpen = !overviewOpen"
            >
              <span class="text-sm font-semibold text-ink-gray-9">Overview</span>
              <Icon
                name="chevron-down"
                size="13"
                class="text-ink-gray-5 transition-transform duration-200"
                :class="{ 'rotate-180': !overviewOpen }"
              />
            </div>

            <div v-show="overviewOpen" class="space-y-2.5 text-sm pt-1">
              <!-- 1. Assignee Row with Interactive Picker -->
              <div class="flex items-center gap-2 relative">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Assignee</span>
                <div class="flex-1 min-w-0">
                  <div
                    @click="showAssigneePicker = !showAssigneePicker"
                    class="flex items-center justify-between px-2.5 py-1.5 -ms-2 rounded-xl hover:bg-surface-gray-2 cursor-pointer transition select-none group"
                  >
                    <div class="flex items-center gap-1.5 min-w-0">
                      <template v-if="task.assignees?.length > 0">
                        <Avatar :label="task.assignees[0].full_name || task.assignees[0].email" size="sm" />
                        <span class="font-medium text-ink-gray-8 truncate">
                          {{ task.assignees[0].full_name || task.assignees[0].email }}
                        </span>
                        <span v-if="task.assignees.length > 1" class="text-xs text-ink-gray-5 font-mono">
                          +{{ task.assignees.length - 1 }}
                        </span>
                      </template>
                      <template v-else>
                        <span class="text-ink-gray-4 italic">Set Assignee...</span>
                      </template>
                    </div>
                    <Icon name="chevron-down" size="12" class="text-ink-gray-4 group-hover:text-ink-gray-7 shrink-0 transition-transform" :class="{ 'rotate-180': showAssigneePicker }" />
                  </div>

                  <!-- Assignee Dropdown Picker Popover -->
                  <div
                    v-if="showAssigneePicker"
                    class="absolute left-0 top-full mt-1.5 w-64 !bg-white border border-outline-gray-2 rounded-2xl shadow-xl z-50 p-2.5 space-y-2 animate-in fade-in duration-100"
                  >
                    <!-- Search user -->
                    <div class="px-1">
                      <input
                        v-model="assigneeSearch"
                        type="text"
                        placeholder="Search users..."
                        class="w-full px-3 py-1.5 text-sm rounded-xl border border-outline-gray-2 bg-surface-gray-1 focus:outline-none focus:bg-surface-white transition shadow-2xs"
                        @click.stop
                      />
                    </div>

                    <!-- User Options List -->
                    <div class="max-h-48 overflow-y-auto space-y-0.5">
                      <div
                        v-for="u in filteredUsers"
                        :key="u.name"
                        @click.stop="toggleAssignee(u)"
                        class="px-2.5 py-1.5 rounded-xl flex items-center justify-between hover:bg-surface-gray-2 cursor-pointer transition text-sm"
                      >
                        <div class="flex items-center gap-2 min-w-0">
                          <Avatar :label="u.full_name || u.name" size="sm" />
                          <div class="truncate">
                            <div class="font-medium text-ink-gray-9 truncate">{{ u.full_name || u.name }}</div>
                            <div class="text-xs text-ink-gray-4 truncate">{{ u.name }}</div>
                          </div>
                        </div>

                        <!-- Checkmark if assigned -->
                        <span v-if="isAssigned(u.name)" class="text-blue-600 font-bold shrink-0">✓</span>
                      </div>
                    </div>

                    <div class="pt-1.5 border-t border-outline-gray-1 flex justify-end">
                      <Button variant="ghost" size="sm" label="Close" class="!px-2.5 !py-0.5 rounded-lg" @click="showAssigneePicker = false" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- 2. Priority Row (Interactive Dropdown) -->
              <div class="flex items-center gap-2">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Priority</span>
                <div class="flex-1 min-w-0">
                  <Dropdown :options="priorityDropdownOptions" align="start">
                    <template #default="{ open }">
                      <div class="flex items-center justify-between px-2.5 py-1.5 -ms-2 rounded-xl hover:bg-surface-gray-2 cursor-pointer transition select-none group">
                        <div class="flex items-center gap-1.5 min-w-0">
                          <TicketPriority :priority="task.priority || 'Medium'" />
                        </div>
                        <Icon name="chevron-down" size="12" class="text-ink-gray-4 group-hover:text-ink-gray-7 shrink-0 transition-transform" :class="{ 'rotate-180': open }" />
                      </div>
                    </template>
                  </Dropdown>
                </div>
              </div>

              <!-- 3. Module Row (Interactive Dropdown) -->
              <div class="flex items-center gap-2">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Module</span>
                <div class="flex-1 min-w-0">
                  <Dropdown :options="moduleDropdownOptions" align="start">
                    <template #default="{ open }">
                      <div class="flex items-center justify-between px-2.5 py-1.5 -ms-2 rounded-xl hover:bg-surface-gray-2 cursor-pointer transition select-none group">
                        <span class="font-medium text-ink-gray-8 truncate">
                          {{ task.module_title || 'General' }}
                        </span>
                        <Icon name="chevron-down" size="12" class="text-ink-gray-4 group-hover:text-ink-gray-7 shrink-0 transition-transform" :class="{ 'rotate-180': open }" />
                      </div>
                    </template>
                  </Dropdown>
                </div>
              </div>

              <!-- 4. Customer Row (Interactive Editor) -->
              <div class="flex items-center gap-2 relative">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Customer</span>
                <div class="flex-1 min-w-0">
                  <div
                    v-if="!editingCustomer"
                    @click="startCustomerEdit"
                    class="flex items-center justify-between px-2.5 py-1.5 -ms-2 rounded-xl hover:bg-surface-gray-2 cursor-pointer transition select-none group"
                  >
                    <span class="font-medium text-ink-gray-8 truncate">
                      {{ task.client_poc_name || 'Set Customer...' }}
                    </span>
                    <Icon name="edit-2" size="11" class="text-ink-gray-4 group-hover:text-ink-gray-7 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <div v-else class="flex items-center gap-1.5">
                    <input
                      ref="customerInputRef"
                      v-model="customerText"
                      @keydown.enter="saveCustomerEdit"
                      @keydown.escape="editingCustomer = false"
                      class="flex-1 px-3 py-1.5 text-sm rounded-xl border border-outline-gray-3 bg-surface-white focus:outline-none transition shadow-2xs"
                    />
                    <button @click="saveCustomerEdit" class="text-sm text-emerald-600 font-bold px-2 py-1 rounded-lg hover:bg-emerald-50">✓</button>
                    <button @click="editingCustomer = false" class="text-sm text-ink-gray-4 px-2 py-1 rounded-lg hover:bg-surface-gray-2">✕</button>
                  </div>
                </div>
              </div>

              <!-- 5. Project Row (Interactive Dropdown) -->
              <div class="flex items-center gap-2">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Project</span>
                <div class="flex-1 min-w-0">
                  <Dropdown :options="projectDropdownOptions" align="start">
                    <template #default="{ open }">
                      <div class="flex items-center justify-between px-2.5 py-1.5 -ms-2 rounded-xl hover:bg-surface-gray-2 cursor-pointer transition select-none group">
                        <span class="font-medium text-ink-gray-8 truncate">
                          {{ task.project_title || 'Select Project...' }}
                        </span>
                        <Icon name="chevron-down" size="12" class="text-ink-gray-4 group-hover:text-ink-gray-7 shrink-0 transition-transform" :class="{ 'rotate-180': open }" />
                      </div>
                    </template>
                  </Dropdown>
                </div>
              </div>

              <!-- 6. Tags Row (Interactive Chips + Add Tag) -->
              <div class="flex items-start gap-2 pt-1">
                <span class="w-[106px] shrink-0 text-ink-gray-5 pt-0.5">Tags</span>
                <div class="flex-1 min-w-0 flex flex-wrap items-center gap-1.5">
                  <span
                    v-for="tag in (task.tags || [])"
                    :key="tag"
                    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs bg-surface-gray-2 text-ink-gray-7 border border-outline-gray-2"
                  >
                    <span>{{ tag }}</span>
                    <button @click.stop="handleRemoveTag(tag)" class="text-ink-gray-4 hover:text-ink-gray-9 text-sm font-bold leading-none">×</button>
                  </span>

                  <!-- Inline Add Tag Input -->
                  <div v-if="showTagInput" class="inline-flex items-center gap-1.5">
                    <input
                      ref="tagInputRef"
                      v-model="newTagText"
                      @keydown.enter.prevent="handleAddTag"
                      @keydown.escape="showTagInput = false"
                      placeholder="Tag..."
                      class="w-24 px-2.5 py-1 text-xs rounded-xl border border-outline-gray-3 bg-surface-white focus:outline-none transition shadow-2xs"
                    />
                    <button @click="handleAddTag" class="text-xs text-ink-gray-8 font-medium px-2 py-0.5 rounded-lg hover:bg-surface-gray-2">Add</button>
                    <button @click="showTagInput = false" class="text-xs text-ink-gray-4 px-1.5 py-0.5 rounded-lg hover:bg-surface-gray-2">✕</button>
                  </div>
                  <Button
                    v-else
                    variant="ghost"
                    size="sm"
                    label="+ Add"
                    class="!px-2 !py-0.5 rounded-lg text-ink-gray-6 hover:text-ink-gray-9"
                    @click="openTagInput"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Section 2: More Details (Collapsible matching Helpdesk) -->
          <div class="p-4 space-y-3">
            <div
              class="flex items-center justify-between cursor-pointer select-none"
              @click="moreDetailsOpen = !moreDetailsOpen"
            >
              <span class="text-sm font-semibold text-ink-gray-9">More Details</span>
              <Icon
                name="chevron-down"
                size="13"
                class="text-ink-gray-5 transition-transform duration-200"
                :class="{ 'rotate-180': !moreDetailsOpen }"
              />
            </div>

            <div v-show="moreDetailsOpen" class="space-y-2.5 text-sm pt-1">
              <!-- Due Date -->
              <div class="flex items-center gap-2">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Due Date</span>
                <input
                  type="date"
                  :value="cleanDate(task.exp_end_date)"
                  @change="e => handleGenericUpdate('exp_end_date', e.target.value)"
                  class="flex-1 px-2.5 py-1 text-sm rounded-xl border border-outline-gray-2 bg-surface-white text-ink-gray-8 focus:outline-none focus:border-outline-gray-4"
                />
              </div>

              <!-- Start Date -->
              <div class="flex items-center gap-2">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Start Date</span>
                <input
                  type="date"
                  :value="cleanDate(task.exp_start_date)"
                  @change="e => handleGenericUpdate('exp_start_date', e.target.value)"
                  class="flex-1 px-2.5 py-1 text-sm rounded-xl border border-outline-gray-2 bg-surface-white text-ink-gray-8 focus:outline-none focus:border-outline-gray-4"
                />
              </div>

              <!-- Estimated Hours -->
              <div class="flex items-center gap-2">
                <span class="w-[106px] shrink-0 text-ink-gray-5">Est. Hours</span>
                <input
                  type="number"
                  :value="task.expected_time || 0"
                  @change="e => handleGenericUpdate('expected_time', parseFloat(e.target.value) || 0)"
                  class="w-20 px-2.5 py-1 text-sm rounded-xl border border-outline-gray-2 bg-surface-white text-ink-gray-8 focus:outline-none"
                />
              </div>

              <!-- Key Milestone Toggle -->
              <div class="flex items-center justify-between pt-1">
                <span class="text-ink-gray-7">Key Milestone</span>
                <input
                  type="checkbox"
                  :checked="Boolean(task.is_milestone)"
                  @change="e => handleGenericUpdate('is_milestone', e.target.checked ? 1 : 0)"
                  class="rounded-md border-outline-gray-3 text-ink-gray-9 focus:ring-0"
                />
              </div>

              <!-- Client Visible Toggle -->
              <div class="flex items-center justify-between">
                <span class="text-ink-gray-7">Client Visible</span>
                <input
                  type="checkbox"
                  :checked="Boolean(task.client_visible)"
                  @change="e => handleGenericUpdate('client_visible', e.target.checked ? 1 : 0)"
                  class="rounded-md border-outline-gray-3 text-ink-gray-9 focus:ring-0"
                />
              </div>
            </div>
          </div>

          <!-- Section 3: Recent Tasks -->
          <div class="p-4 space-y-3">
            <div
              class="flex items-center justify-between cursor-pointer select-none"
              @click="recentTicketsOpen = !recentTicketsOpen"
            >
              <span class="text-sm font-semibold text-ink-gray-9">Recent Tasks</span>
              <Icon
                name="chevron-down"
                size="13"
                class="text-ink-gray-5 transition-transform duration-200"
                :class="{ 'rotate-180': !recentTicketsOpen }"
              />
            </div>

            <div v-show="recentTicketsOpen" class="space-y-1.5 pt-1">
              <div
                v-for="item in recentTasksList"
                :key="item.name"
                @click="$router.push('/tasks/' + item.name)"
                class="p-2.5 rounded-xl hover:bg-surface-gray-2 cursor-pointer transition space-y-1"
              >
                <div class="flex items-start justify-between gap-1">
                  <div class="font-medium text-sm text-ink-gray-9 truncate leading-snug">
                    {{ item.subject }}
                  </div>
                  <Badge
                    size="sm"
                    variant="subtle"
                    :theme="item.status === 'Open' ? 'red' : item.status === 'Working' ? 'blue' : 'gray'"
                    :label="item.status === 'Working' ? 'Replied' : item.status"
                  />
                </div>
                <div class="text-xs text-ink-gray-4">
                  {{ formatDate(item.exp_end_date) || '22-10-2026' }} • #{{ item.name?.split('-')?.pop() || '0200' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { toast } from 'frappe-ui'
import Icon from './Icon.vue'
import ActivityIcon from './icons/ActivityIcon.vue'
import EmailIcon from './icons/EmailIcon.vue'
import CommentIcon from './icons/CommentIcon.vue'
import IndicatorIcon from './icons/IndicatorIcon.vue'
import TicketPriority from './TicketPriority.vue'
import CommunicationArea from './CommunicationArea.vue'
import TaskActivities from './TaskActivities.vue'
import {
  getTask,
  updateTask,
  getTasks,
  getUsers,
  getImplementationModules,
  getProjects,
  assignTask,
} from '../api'

const props = defineProps({
  taskId: {
    type: String,
    required: true,
  },
  showBack: {
    type: Boolean,
    default: true,
  },
  showClose: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['back', 'close', 'updated'])

const task = ref({})
const activeTab = ref('activity')
const commAreaRef = ref(null)
const overviewOpen = ref(true)
const moreDetailsOpen = ref(false)
const recentTicketsOpen = ref(true)

const emailTimeline = computed(() => {
  return (task.value.activity_timeline || []).filter(item => item.type === 'communication')
})

const commentTimeline = computed(() => {
  return (task.value.activity_timeline || []).filter(item => item.type === 'comment')
})

const emailCount = computed(() => emailTimeline.value.length)
const commentCount = computed(() => commentTimeline.value.length)

// ---------------------------------------------------------------------------
// Helpdesk-style activity feed (oldest first, newest at the bottom)
// ---------------------------------------------------------------------------
const feedRef = ref(null)

const allActivities = computed(() => {
  const t = task.value || {}
  if (!t.name) return []
  const items = []

  // Task description = the opening entry (like a ticket's first message)
  items.push({
    key: 'description',
    type: 'description',
    user: t.owner,
    userName: t.owner_name || t.owner,
    userImage: t.owner_image,
    content: t.description_html,
    timestamp: t.creation,
  })

  for (const item of t.activity_timeline || []) {
    if (item.type === 'communication') {
      items.push({
        key: 'email-' + item.id,
        id: item.id,
        type: 'email',
        user: item.sender,
        userName: item.sender_name || item.sender,
        userImage: item.sender_image,
        recipients: item.recipients,
        subject: item.subject,
        content: item.content,
        timestamp: item.timestamp,
      })
    } else if (item.type === 'comment') {
      items.push({
        key: 'comment-' + item.id,
        id: item.id,
        type: 'comment',
        user: item.sender,
        userName: item.sender_name || item.sender,
        userImage: item.sender_image,
        content: item.content,
        timestamp: item.timestamp,
      })
    } else if (item.type === 'system' && item.action !== 'created') {
      // "<Name> assigned bala: demo" -> name + action
      const name = item.sender_name || item.sender || ''
      const text = item.content || ''
      items.push({
        key: 'history-' + item.id,
        type: 'history',
        kind: item.action,
        user: item.sender,
        userName: name,
        action: name && text.startsWith(name) ? text.slice(name.length).trim() : text,
        timestamp: item.timestamp,
      })
    }
  }

  for (const v of t.viewers || []) {
    items.push({
      key: 'view-' + v.user,
      type: 'history',
      kind: 'view',
      user: v.user,
      userName: v.full_name || v.user,
      action: 'viewed this',
      timestamp: v.last_viewed,
    })
  }

  return items.sort((x, y) => String(x.timestamp || '').localeCompare(String(y.timestamp || '')))
})

const currentActivities = computed(() => {
  if (activeTab.value === 'emails') return allActivities.value.filter((a) => a.type === 'email')
  if (activeTab.value === 'comments') return allActivities.value.filter((a) => a.type === 'comment')
  // Activity tab: emails, comments, assignment changes and views
  return allActivities.value.filter(
    (a) =>
      a.type === 'email' ||
      a.type === 'comment' ||
      (a.type === 'history' && ACTIVITY_KINDS.includes(a.kind))
  )
})

const ACTIVITY_KINDS = ['assigned', 'assignment completed', 'view']

const tabTitle = computed(() => {
  if (activeTab.value === 'emails') return 'Emails'
  if (activeTab.value === 'comments') return 'Comments'
  if (activeTab.value === 'analytics') return 'Analytics'
  return 'Activity'
})

const emptyState = computed(() => {
  if (activeTab.value === 'emails') return { text: 'No emails', icon: 'email' }
  if (activeTab.value === 'comments') return { text: 'No comments', icon: 'comment' }
  return { text: 'No activities', icon: 'activity' }
})

const newActivityOptions = computed(() => [
  { label: 'Email', onClick: () => commAreaRef.value?.expandReply(task.value.client_poc_email) },
  { label: 'Comment', onClick: () => commAreaRef.value?.expandComment() },
])

function scrollFeedToBottom() {
  nextTick(() => {
    if (feedRef.value) feedRef.value.scrollTop = feedRef.value.scrollHeight
  })
}

watch(activeTab, () => scrollFeedToBottom())

function onReplyToEmail(activity, replyAll) {
  const me = window.session_user || ''
  let recipients = [activity.user]
  if (replyAll && activity.recipients) {
    recipients.push(...String(activity.recipients).split(',').map((r) => r.trim()))
  }
  recipients = [...new Set(recipients.filter((r) => r && r !== me))]
  if (!recipients.length) recipients = [activity.user]
  recipients.forEach((r) => commAreaRef.value?.expandReply(r))
}

function onCommentUpdated(commentId, html) {
  const item = (task.value.activity_timeline || []).find((i) => i.type === 'comment' && i.id === commentId)
  if (item && html !== undefined) item.content = html
}

function onCommentDeleted(commentId) {
  task.value.activity_timeline = (task.value.activity_timeline || []).filter(
    (i) => !(i.type === 'comment' && i.id === commentId)
  )
}

const availableUsers = ref([])
const availableModules = ref([])
const availableProjects = ref([])

// Assignee Picker
const showAssigneePicker = ref(false)
const assigneeSearch = ref('')

// Customer Edit
const editingCustomer = ref(false)
const customerText = ref('')
const customerInputRef = ref(null)

// Tags Edit
const showTagInput = ref(false)
const newTagText = ref('')
const tagInputRef = ref(null)

const recentTasksList = ref([])

const statusOptions = computed(() => [
  { label: 'Open', onClick: () => updateStatus('Open') },
  { label: 'Working', onClick: () => updateStatus('Working') },
  { label: 'Pending Review', onClick: () => updateStatus('Pending Review') },
  { label: 'Completed', onClick: () => updateStatus('Completed') },
  { label: 'Cancelled', onClick: () => updateStatus('Cancelled') },
])

const moreOptions = computed(() => [
  { label: 'Copy Task ID', onClick: () => navigator.clipboard.writeText(task.value.name) },
  { label: 'Open in Desk', onClick: () => window.open('/app/task/' + task.value.name, '_blank') },
])

const priorityDropdownOptions = computed(() => [
  { label: 'Low', onClick: () => handleGenericUpdate('priority', 'Low') },
  { label: 'Medium', onClick: () => handleGenericUpdate('priority', 'Medium') },
  { label: 'High', onClick: () => handleGenericUpdate('priority', 'High') },
  { label: 'Urgent', onClick: () => handleGenericUpdate('priority', 'Urgent') },
])

const moduleDropdownOptions = computed(() => {
  return availableModules.value.map(m => ({
    label: m.module_name,
    onClick: () => handleModuleSelect(m),
  }))
})

const projectDropdownOptions = computed(() => {
  return availableProjects.value.map(p => ({
    label: p.project_name,
    onClick: () => handleProjectSelect(p),
  }))
})

const filteredUsers = computed(() => {
  if (!assigneeSearch.value.trim()) return availableUsers.value
  const q = assigneeSearch.value.toLowerCase()
  return availableUsers.value.filter(u =>
    (u.full_name || '').toLowerCase().includes(q) || (u.name || '').toLowerCase().includes(q)
  )
})

onMounted(async () => {
  await Promise.all([
    loadTask(),
    loadRecentTasks(),
    loadMetadata(),
  ])
})

watch(() => props.taskId, async () => {
  await loadTask()
  await loadRecentTasks()
})

async function loadMetadata() {
  try {
    const [uList, mList, pList] = await Promise.all([
      getUsers(),
      getImplementationModules(),
      getProjects(),
    ])
    availableUsers.value = uList || []
    availableModules.value = mList || []
    availableProjects.value = pList || []
  } catch (e) {
    console.error('Failed to load sidebar metadata', e)
  }
}

async function loadTask() {
  if (!props.taskId) return
  try {
    const data = await getTask(props.taskId)
    task.value = data
    customerText.value = data.client_poc_name || ''
    scrollFeedToBottom()
  } catch (e) {
    console.error('Failed to load task', e)
  }
}

async function loadRecentTasks() {
  try {
    const list = await getTasks({ limit: 4 })
    recentTasksList.value = list.filter(t => t.name !== props.taskId).slice(0, 4)
  } catch (e) {}
}

function isAssigned(userEmail) {
  return Boolean(
    task.value.assignee_emails?.includes(userEmail) ||
    task.value.assignees?.some(a => a.email === userEmail)
  )
}

async function toggleAssignee(user) {
  const email = user.name
  const assigned = isAssigned(email)
  try {
    await assignTask(task.value.name, email, assigned ? 'remove' : 'add')
    if (assigned) {
      task.value.assignees = (task.value.assignees || []).filter(a => a.email !== email)
      task.value.assignee_emails = (task.value.assignee_emails || []).filter(e => e !== email)
    } else {
      if (!task.value.assignees) task.value.assignees = []
      if (!task.value.assignee_emails) task.value.assignee_emails = []
      task.value.assignees.push({
        email: email,
        full_name: user.full_name || email,
        user_image: user.user_image,
      })
      task.value.assignee_emails.push(email)
    }
    emit('updated')
    toast.success('Assignee updated')
  } catch (e) {
    toast.error('Failed to update assignee: ' + (e.message || e))
  }
}

async function handleGenericUpdate(fieldName, value) {
  try {
    await updateTask(task.value.name, { [fieldName]: value })
    task.value[fieldName] = value
    emit('updated')
    toast.success('Task updated')
  } catch (e) {
    toast.error(`Failed to update ${fieldName}: ` + (e.message || e))
  }
}

async function handleModuleSelect(m) {
  try {
    await updateTask(task.value.name, { implementation_module: m.name })
    task.value.implementation_module = m.name
    task.value.module_title = m.module_name
    task.value.module_icon = m.icon
    task.value.module_color = m.color
    emit('updated')
    toast.success('Module updated')
  } catch (e) {
    toast.error('Failed to update module: ' + (e.message || e))
  }
}

async function handleProjectSelect(p) {
  try {
    await updateTask(task.value.name, { project: p.name })
    task.value.project = p.name
    task.value.project_title = p.project_name
    task.value.client_poc_name = p.client_poc_name
    emit('updated')
    toast.success('Project updated')
  } catch (e) {
    toast.error('Failed to update project: ' + (e.message || e))
  }
}

function startCustomerEdit() {
  customerText.value = task.value.client_poc_name || ''
  editingCustomer.value = true
  nextTick(() => {
    customerInputRef.value?.focus()
  })
}

async function saveCustomerEdit() {
  const val = customerText.value.trim()
  editingCustomer.value = false
  if (val !== task.value.client_poc_name) {
    await handleGenericUpdate('client_poc_name', val)
  }
}

function openTagInput() {
  showTagInput.value = true
  newTagText.value = ''
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

async function handleAddTag() {
  const tag = newTagText.value.trim()
  if (!tag) {
    showTagInput.value = false
    return
  }
  if (!task.value.tags) task.value.tags = []
  if (!task.value.tags.includes(tag)) {
    task.value.tags.push(tag)
    try {
      await updateTask(task.value.name, { tags: task.value.tags })
      emit('updated')
      toast.success('Tag added')
    } catch (e) {
      toast.error('Failed to add tag: ' + (e.message || e))
    }
  }
  newTagText.value = ''
  showTagInput.value = false
}

async function handleRemoveTag(tagToRemove) {
  task.value.tags = (task.value.tags || []).filter(t => t !== tagToRemove)
  try {
    await updateTask(task.value.name, { tags: task.value.tags })
    emit('updated')
    toast.success('Tag removed')
  } catch (e) {
    toast.error('Failed to remove tag: ' + (e.message || e))
  }
}

async function updateStatus(s) {
  try {
    await updateTask(task.value.name, { status: s })
    task.value.status = s
    emit('updated')
    toast.success('Status updated to ' + s)
  } catch (e) {
    toast.error('Failed to update status: ' + (e.message || e))
  }
}

async function onCommunicationSubmitted() {
  await loadTask()
  emit('updated')
}

function statusDotClass(status) {
  switch (status) {
    case 'Completed':
      return 'text-emerald-500'
    case 'Working':
      return 'text-blue-500'
    case 'Pending Review':
      return 'text-amber-500'
    default:
      return 'text-blue-500'
  }
}

function cleanDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.split(' ')[0]
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr.split(' ')[0])
    if (isNaN(d.getTime())) return dateStr
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>
