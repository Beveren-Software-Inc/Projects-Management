<template>
  <div class="h-full flex flex-col bg-surface-gray-2 overflow-hidden">
    <!-- Top Filter Bar -->
    <div class="px-6 py-2.5 bg-white border-b border-outline-gray-2 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-2">
        <span class="text-xs font-semibold text-ink-gray-7">Kanban Board</span>
        <span class="text-xs text-ink-gray-4">({{ tasks.length }} total tasks)</span>
      </div>

      <div class="flex items-center gap-2 text-xs">
        <select
          v-model="selectedModule"
          @change="$emit('filter-change', { module: selectedModule, priority: selectedPriority })"
          class="px-3 py-1.5 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white text-ink-gray-7 focus:outline-none transition shadow-2xs cursor-pointer"
        >
          <option value="All">All Modules</option>
          <option v-for="m in modules" :key="m.module_code" :value="m.module_code">
            {{ m.module_name }}
          </option>
        </select>

        <select
          v-model="selectedPriority"
          @change="$emit('filter-change', { module: selectedModule, priority: selectedPriority })"
          class="px-3 py-1.5 text-xs rounded-xl border border-outline-gray-2 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-white text-ink-gray-7 focus:outline-none transition shadow-2xs cursor-pointer"
        >
          <option value="All">All Priorities</option>
          <option value="Urgent">Urgent</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </div>
    </div>

    <!-- Kanban Columns Grid -->
    <div class="flex-1 p-6 overflow-x-auto flex gap-5">
      <div
        v-for="col in columns"
        :key="col.id"
        class="w-80 shrink-0 flex flex-col bg-surface-gray-1 rounded-2xl border border-outline-gray-2 shadow-2xs max-h-full overflow-hidden"
      >
        <!-- Column Header -->
        <div class="px-4 py-3 border-b border-outline-gray-2 bg-white flex items-center justify-between shrink-0 rounded-t-2xl">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" :class="col.dotClass"></span>
            <span class="font-semibold text-xs text-ink-gray-9">{{ col.title }}</span>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-surface-gray-2 text-ink-gray-6">
            {{ getTasksByStatus(col.id).length }}
          </span>
        </div>

        <!-- Column Cards Container -->
        <div class="flex-1 p-3 overflow-y-auto space-y-3">
          <div
            v-if="getTasksByStatus(col.id).length === 0"
            class="py-12 text-center text-xs text-ink-gray-4 border border-dashed border-outline-gray-2 rounded-xl"
          >
            No tasks in {{ col.title }}
          </div>

          <!-- Task Card -->
          <div
            v-for="task in getTasksByStatus(col.id)"
            :key="task.name"
            @click="$emit('select-task', task.name)"
            class="p-3.5 bg-white rounded-2xl border border-outline-gray-2 hover:border-blue-400 hover:shadow-md transition cursor-pointer select-none space-y-2.5 group"
          >
            <!-- Card Top: Module & Priority -->
            <div class="flex items-center justify-between">
              <span
                v-if="task.module_title"
                class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold"
                :style="{ backgroundColor: (task.module_color || '#3B82F6') + '18', color: task.module_color || '#3B82F6' }"
              >
                <Icon :name="task.module_icon || 'package'" size="10" />
                <span>{{ task.module_title }}</span>
              </span>
              <span v-else class="text-[10px] text-ink-gray-4">General</span>

              <div class="flex items-center gap-1">
                <span
                  v-if="task.is_milestone"
                  class="p-0.5 text-amber-500"
                  title="Key Milestone"
                >
                  <Icon name="flag" size="12" />
                </span>
                <span
                  class="px-2 py-0.5 rounded-md text-[10px] font-semibold"
                  :class="priorityBadgeClass(task.priority)"
                >
                  {{ task.priority }}
                </span>
              </div>
            </div>

            <!-- Card Body: Subject -->
            <div>
              <div class="text-[11px] font-mono text-ink-gray-4 mb-0.5">{{ task.name }}</div>
              <h4 class="font-medium text-xs text-ink-gray-9 leading-snug group-hover:text-blue-600 transition">
                {{ task.subject }}
              </h4>
              <div class="text-[11px] text-ink-gray-5 mt-1 font-medium truncate">
                {{ task.project_title || task.project }}
              </div>
            </div>

            <!-- Card Bottom: Dates, Progress, Assignees -->
            <div class="pt-2 border-t border-outline-gray-1 flex items-center justify-between">
              <!-- Due date -->
              <div class="flex items-center gap-1 text-[11px]" :class="task.is_overdue ? 'text-red-600 font-semibold' : 'text-ink-gray-5'">
                <Icon name="clock" size="11" />
                <span>{{ task.exp_end_date ? formatDate(task.exp_end_date) : 'No due date' }}</span>
              </div>

              <!-- Assignee avatar -->
              <div class="flex items-center gap-1.5">
                <div v-if="task.assignees?.length > 0" class="flex -space-x-1.5">
                  <div
                    v-for="u in task.assignees"
                    :key="u.email"
                    class="w-5 h-5 rounded-full bg-blue-100 text-blue-700 font-bold text-[8px] flex items-center justify-center ring-2 ring-white shrink-0"
                    :title="u.full_name || u.email"
                  >
                    {{ getInitials(u.full_name || u.email) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Move Controls -->
            <div class="pt-2 flex items-center justify-between border-t border-dashed border-outline-gray-1 text-[11px]" @click.stop>
              <span class="text-ink-gray-4">Move:</span>
              <div class="flex gap-1">
                <button
                  v-if="col.id !== 'Open'"
                  @click="$emit('update-status', task.name, 'Open')"
                  class="px-2 py-0.5 text-[10px] rounded-md hover:bg-surface-gray-2 text-ink-gray-6 transition"
                  title="Move to Open"
                >
                  ← Open
                </button>
                <button
                  v-if="col.id !== 'Working'"
                  @click="$emit('update-status', task.name, 'Working')"
                  class="px-2 py-0.5 text-[10px] rounded-md hover:bg-blue-50 text-blue-600 font-medium transition"
                  title="Move to Working"
                >
                  Working
                </button>
                <button
                  v-if="col.id !== 'Pending Review'"
                  @click="$emit('update-status', task.name, 'Pending Review')"
                  class="px-2 py-0.5 text-[10px] rounded-md hover:bg-amber-50 text-amber-600 font-medium transition"
                  title="Move to Review"
                >
                  Review
                </button>
                <button
                  v-if="col.id !== 'Completed'"
                  @click="$emit('update-status', task.name, 'Completed')"
                  class="px-2 py-0.5 text-[10px] rounded-md hover:bg-emerald-50 text-emerald-600 font-medium transition"
                  title="Mark Completed"
                >
                  Done ✓
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => [],
  },
  modules: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['select-task', 'update-status', 'filter-change'])

const selectedModule = ref('All')
const selectedPriority = ref('All')

const columns = [
  { id: 'Open', title: 'Open / Backlog', dotClass: 'bg-surface-gray-5' },
  { id: 'Working', title: 'In Progress (Working)', dotClass: 'bg-blue-500' },
  { id: 'Pending Review', title: 'Pending Review / UAT', dotClass: 'bg-amber-500' },
  { id: 'Completed', title: 'Completed', dotClass: 'bg-emerald-500' },
]

function getTasksByStatus(status) {
  return props.tasks.filter(t => t.status === status)
}

function priorityBadgeClass(priority) {
  switch (priority) {
    case 'Urgent':
      return 'bg-red-100 text-red-800'
    case 'High':
      return 'bg-orange-100 text-orange-800'
    case 'Medium':
      return 'bg-blue-50 text-blue-700'
    default:
      return 'bg-surface-gray-2 text-ink-gray-6'
  }
}

function getInitials(name) {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.substring(0, 2).toUpperCase()
}

function formatDate(dateStr) {
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

