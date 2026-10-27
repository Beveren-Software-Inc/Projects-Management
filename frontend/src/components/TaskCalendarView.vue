<template>
  <div class="h-full flex flex-col bg-surface-white overflow-hidden">
    <!-- Calendar Controls Header -->
    <div class="px-6 py-3 border-b border-outline-gray-2 bg-white flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <h2 class="text-sm font-semibold text-ink-gray-9">{{ currentMonthLabel }}</h2>
        <div class="flex items-center rounded-xl border border-outline-gray-3 overflow-hidden shadow-2xs">
          <button
            @click="prevMonth"
            class="px-2.5 py-1 text-ink-gray-6 hover:bg-surface-gray-2 border-r border-outline-gray-3 transition"
          >
            <Icon name="chevron-left" size="14" />
          </button>
          <button
            @click="goToToday"
            class="px-3 py-1 text-xs font-medium text-ink-gray-7 hover:bg-surface-gray-2 transition"
          >
            Today
          </button>
          <button
            @click="nextMonth"
            class="px-2.5 py-1 text-ink-gray-6 hover:bg-surface-gray-2 border-l border-outline-gray-3 transition"
          >
            <Icon name="chevron-right" size="14" />
          </button>
        </div>
      </div>

      <!-- Filters: My Tasks vs All -->
      <div class="flex items-center gap-3 text-xs">
        <div class="flex items-center p-0.5 bg-surface-gray-2 rounded-xl border border-outline-gray-2">
          <button
            @click="filterMyTasks = false; emitFilter()"
            class="px-3 py-1 rounded-lg font-medium transition"
            :class="!filterMyTasks ? 'bg-white shadow-xs text-ink-gray-9 font-semibold' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          >
            All Tasks
          </button>
          <button
            @click="filterMyTasks = true; emitFilter()"
            class="px-3 py-1 rounded-lg font-medium transition flex items-center gap-1.5"
            :class="filterMyTasks ? 'bg-white shadow-xs text-ink-gray-9 font-semibold' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          >
            <Icon name="user" size="12" />
            <span>Assigned to Me</span>
          </button>
        </div>

        <span class="text-ink-gray-5">
          {{ filteredCalendarTasks.length }} tasks scheduled this month
        </span>
      </div>
    </div>

    <!-- Calendar Weekday Header -->
    <div class="grid grid-cols-7 border-b border-outline-gray-2 bg-surface-gray-1 text-center text-[11px] font-semibold text-ink-gray-5 py-2 select-none shrink-0">
      <div>Sun</div>
      <div>Mon</div>
      <div>Tue</div>
      <div>Wed</div>
      <div>Thu</div>
      <div>Fri</div>
      <div>Sat</div>
    </div>

    <!-- Calendar Month Grid -->
    <div class="flex-1 grid grid-cols-7 auto-rows-fr overflow-y-auto divide-x divide-y divide-outline-gray-2 bg-surface-gray-2/20">
      <div
        v-for="cell in calendarCells"
        :key="cell.dateKey"
        class="min-h-[110px] p-2 bg-white flex flex-col transition hover:bg-blue-50/20"
        :class="{
          'bg-surface-gray-1/60 text-ink-gray-4': !cell.isCurrentMonth,
          'ring-2 ring-blue-500 ring-inset z-10': cell.isToday,
        }"
      >
        <!-- Date Number -->
        <div class="flex items-center justify-between mb-1.5 shrink-0 select-none">
          <span
            class="text-xs font-semibold px-1.5 py-0.2 rounded-md"
            :class="cell.isToday ? 'bg-blue-600 text-white' : 'text-ink-gray-7'"
          >
            {{ cell.dayNumber }}
          </span>
          <span v-if="cell.tasks.length > 0" class="text-[10px] text-ink-gray-4 font-medium">
            {{ cell.tasks.length }}
          </span>
        </div>

        <!-- Task Pills -->
        <div class="flex-1 overflow-y-auto space-y-1">
          <div
            v-for="task in cell.tasks"
            :key="task.name"
            @click.stop="$emit('select-task', task.name)"
            class="px-2.5 py-1.5 rounded-xl text-[11px] font-medium border cursor-pointer hover:shadow-xs transition truncate select-none flex items-center justify-between group"
            :style="{
              backgroundColor: (task.module_color || '#3B82F6') + '15',
              borderColor: (task.module_color || '#3B82F6') + '40',
              color: task.module_color || '#1E40AF',
            }"
            :title="task.subject + ' (' + (task.status || 'Open') + ')'"
          >
            <div class="flex items-center gap-1 truncate">
              <span v-if="task.is_milestone" class="text-amber-500 shrink-0">★</span>
              <span class="truncate font-medium">{{ task.subject }}</span>
            </div>
            <span
              v-if="task.status === 'Completed'"
              class="text-emerald-600 font-bold ml-1 shrink-0"
            >
              ✓
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['select-task', 'filter-change'])

const currentDate = ref(new Date())
const filterMyTasks = ref(false)

const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())

const currentMonthLabel = computed(() => {
  return currentDate.value.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
})

const currentUser = computed(() => window.session_user || window.boot?.session_user || '')

function prevMonth() {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 1, 1)
}

function nextMonth() {
  currentDate.value = new Date(currentYear.value, currentMonth.value + 1, 1)
}

function goToToday() {
  currentDate.value = new Date()
}

function emitFilter() {
  emit('filter-change', {
    assigned_to: filterMyTasks.value ? currentUser.value : 'All',
  })
}

const filteredCalendarTasks = computed(() => {
  if (!filterMyTasks.value) return props.tasks
  return props.tasks.filter(t => (t.assignee_emails || []).includes(currentUser.value))
})

const calendarCells = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value

  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const prevMonthLastDay = new Date(year, month, 0)

  const firstDayIndex = firstDay.getDay()
  const totalDays = lastDay.getDate()
  const prevMonthTotalDays = prevMonthLastDay.getDate()

  const todayStr = new Date().toISOString().split('T')[0]

  // Map tasks by date
  const taskMap = {}
  for (const t of filteredCalendarTasks.value) {
    const dStr = t.exp_end_date || t.exp_start_date
    if (dStr) {
      if (!taskMap[dStr]) taskMap[dStr] = []
      taskMap[dStr].push(t)
    }
  }

  const cells = []

  // Prev month padding
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const day = prevMonthTotalDays - i
    const d = new Date(year, month - 1, day)
    const dKey = d.toISOString().split('T')[0]
    cells.push({
      dateKey: dKey,
      dayNumber: day,
      isCurrentMonth: false,
      isToday: dKey === todayStr,
      tasks: taskMap[dKey] || [],
    })
  }

  // Current month days
  for (let day = 1; day <= totalDays; day++) {
    const d = new Date(year, month, day)
    const dKey = d.toISOString().split('T')[0]
    cells.push({
      dateKey: dKey,
      dayNumber: day,
      isCurrentMonth: true,
      isToday: dKey === todayStr,
      tasks: taskMap[dKey] || [],
    })
  }

  // Next month padding to reach full 35 or 42 grid
  const remaining = (7 - (cells.length % 7)) % 7
  for (let day = 1; day <= remaining; day++) {
    const d = new Date(year, month + 1, day)
    const dKey = d.toISOString().split('T')[0]
    cells.push({
      dateKey: dKey,
      dayNumber: day,
      isCurrentMonth: false,
      isToday: dKey === todayStr,
      tasks: taskMap[dKey] || [],
    })
  }

  return cells
})
</script>

