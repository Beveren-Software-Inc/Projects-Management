<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    :stroke="color || 'currentColor'"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="inline-block shrink-0"
  >
    <!-- Dashboard -->
    <g v-if="name === 'layout-dashboard' || name === 'dashboard'">
      <rect width="7" height="9" x="3" y="3" rx="1"/>
      <rect width="7" height="5" x="14" y="3" rx="1"/>
      <rect width="7" height="9" x="14" y="12" rx="1"/>
      <rect width="7" height="5" x="3" y="16" rx="1"/>
    </g>

    <!-- Folder Kanban / Projects -->
    <g v-else-if="name === 'folder-kanban' || name === 'projects'">
      <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>
      <path d="M8 10v4"/>
      <path d="M12 10v2"/>
      <path d="M16 10v6"/>
    </g>

    <!-- Tasks / Check Square -->
    <g v-else-if="name === 'check-square' || name === 'tasks'">
      <path d="m9 11 3 3L22 4"/>
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
    </g>

    <!-- Calendar -->
    <g v-else-if="name === 'calendar'">
      <path d="M8 2v4"/>
      <path d="M16 2v4"/>
      <rect width="18" height="18" x="3" y="4" rx="2"/>
      <path d="M3 10h18"/>
    </g>

    <!-- Modules / Blocks / Settings -->
    <g v-else-if="name === 'modules' || name === 'blocks' || name === 'box'">
      <path d="m7.5 4.27 9 5.15"/>
      <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
      <path d="m3.3 7 8.7 5 8.7-5"/>
      <path d="M12 22V12"/>
    </g>

    <!-- Plus -->
    <g v-else-if="name === 'plus'">
      <path d="M5 12h14"/>
      <path d="M12 5v14"/>
    </g>

    <!-- Search -->
    <g v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="8"/>
      <path d="m21 21-4.3-4.3"/>
    </g>

    <!-- User / Contact -->
    <g v-else-if="name === 'user'">
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </g>

    <!-- Users -->
    <g v-else-if="name === 'users' || name === 'Users'">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </g>

    <!-- Mail -->
    <g v-else-if="name === 'mail'">
      <rect width="20" height="16" x="2" y="4" rx="2"/>
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
    </g>

    <!-- Phone -->
    <g v-else-if="name === 'phone'">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
    </g>

    <!-- Tag -->
    <g v-else-if="name === 'tag'">
      <path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/>
      <path d="M7 7h.01"/>
    </g>

    <!-- Clock -->
    <g v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </g>

    <!-- Flag / Priority -->
    <g v-else-if="name === 'flag'">
      <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
      <line x1="4" x2="4" y1="22" y2="15"/>
    </g>

    <!-- Alert Circle / Warning -->
    <g v-else-if="name === 'alert-circle'">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" x2="12" y1="8" y2="12"/>
      <line x1="12" x2="12.01" y1="16" y2="16"/>
    </g>

    <!-- Check Circle / Success -->
    <g v-else-if="name === 'check-circle'">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
      <polyline points="22 4 12 14.01 9 11.01"/>
    </g>

    <!-- Chevron Down -->
    <g v-else-if="name === 'chevron-down'">
      <path d="m6 9 6 6 6-6"/>
    </g>

    <!-- Chevron Right -->
    <g v-else-if="name === 'chevron-right'">
      <path d="m9 18 6-6-6-6"/>
    </g>

    <!-- Chevron Left -->
    <g v-else-if="name === 'chevron-left'">
      <path d="m15 18-6-6 6-6"/>
    </g>

    <!-- X / Close -->
    <g v-else-if="name === 'x'">
      <path d="M18 6 6 18"/>
      <path d="m6 6 12 12"/>
    </g>

    <!-- List -->
    <g v-else-if="name === 'list'">
      <line x1="8" x2="21" y1="6" y2="6"/>
      <line x1="8" x2="21" y1="12" y2="12"/>
      <line x1="8" x2="21" y1="18" y2="18"/>
      <line x1="3" x2="3.01" y1="6" y2="6"/>
      <line x1="3" x2="3.01" y1="12" y2="12"/>
      <line x1="3" x2="3.01" y1="18" y2="18"/>
    </g>

    <!-- Kanban / Columns -->
    <g v-else-if="name === 'kanban'">
      <rect width="6" height="14" x="3" y="5" rx="1"/>
      <rect width="6" height="10" x="11" y="5" rx="1"/>
      <rect width="6" height="18" x="19" y="3" rx="1"/>
    </g>

    <!-- Message Square / Comment -->
    <g v-else-if="name === 'message-square'">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </g>

    <!-- Send -->
    <g v-else-if="name === 'send'">
      <path d="m22 2-7 20-4-9-9-4Z"/>
      <path d="M22 2 11 13"/>
    </g>

    <!-- CreditCard / Accounts -->
    <g v-else-if="name === 'CreditCard' || name === 'credit-card'">
      <rect width="20" height="14" x="2" y="5" rx="2"/>
      <line x1="2" x2="22" y1="10" y2="10"/>
    </g>

    <!-- ShoppingCart / Buying -->
    <g v-else-if="name === 'ShoppingCart' || name === 'shopping-cart'">
      <circle cx="8" cy="21" r="1"/>
      <circle cx="19" cy="21" r="1"/>
      <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>
    </g>

    <!-- TrendingUp / Selling -->
    <g v-else-if="name === 'TrendingUp' || name === 'trending-up'">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
      <polyline points="16 7 22 7 22 13"/>
    </g>

    <!-- Package / Stock -->
    <g v-else-if="name === 'Package' || name === 'package'">
      <path d="m16.5 9.4 4.5-2.8L12 2 3 6.6l4.5 2.8"/>
      <path d="M3 6.6v10.8L12 22l9-4.6V6.6"/>
      <path d="M12 12v10"/>
      <path d="m12 12 4.5-2.6"/>
      <path d="M7.5 9.4 12 12"/>
    </g>

    <!-- Target / CRM -->
    <g v-else-if="name === 'Target' || name === 'target'">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="6"/>
      <circle cx="12" cy="12" r="2"/>
    </g>

    <!-- Cpu / Manufacturing -->
    <g v-else-if="name === 'Cpu' || name === 'cpu'">
      <rect width="16" height="16" x="4" y="4" rx="2"/>
      <rect width="6" height="6" x="9" y="9" rx="1"/>
      <path d="M15 2v2"/>
      <path d="M15 20v2"/>
      <path d="M2 15h2"/>
      <path d="M2 9h2"/>
      <path d="M20 15h2"/>
      <path d="M20 9h2"/>
      <path d="M9 2v2"/>
      <path d="M9 20v2"/>
    </g>

    <!-- LifeBuoy / Helpdesk -->
    <g v-else-if="name === 'LifeBuoy' || name === 'life-buoy'">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="4"/>
      <line x1="4.93" x2="9.17" y1="4.93" y2="9.17"/>
      <line x1="14.83" x2="19.07" y1="14.83" y2="19.07"/>
      <line x1="14.83" x2="19.07" y1="9.17" y2="4.93"/>
      <line x1="4.93" x2="9.17" y1="19.07" y2="14.83"/>
    </g>

    <!-- Server / Assets -->
    <g v-else-if="name === 'Server' || name === 'server'">
      <rect width="20" height="8" x="2" y="2" rx="2" ry="2"/>
      <rect width="20" height="8" x="2" y="14" rx="2" ry="2"/>
      <line x1="6" x2="6.01" y1="6" y2="6"/>
      <line x1="6" x2="6.01" y1="18" y2="18"/>
    </g>

    <!-- Arrow Left -->
    <g v-else-if="name === 'arrow-left'">
      <path d="m12 19-7-7 7-7"/>
      <path d="M19 12H5"/>
    </g>

    <!-- Edit -->
    <g v-else-if="name === 'edit'">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </g>

    <!-- Trash -->
    <g v-else-if="name === 'trash' || name === 'trash-2'">
      <path d="M3 6h18"/>
      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
      <line x1="10" x2="10" y1="11" y2="17"/>
      <line x1="14" x2="14" y1="11" y2="17"/>
    </g>

    <!-- Refresh -->
    <g v-else-if="name === 'refresh' || name === 'refresh-cw'">
      <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
      <path d="M21 3v5h-5"/>
      <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
      <path d="M8 16H3v5"/>
    </g>

    <!-- Check-Check -->
    <g v-else-if="name === 'check-check'">
      <path d="M18 6 7 17l-5-5"/>
      <path d="m22 10-7.5 7.5L13 16"/>
    </g>

    <!-- Bell Off -->
    <g v-else-if="name === 'bell-off'">
      <path d="M8.7 3A6 6 0 0 1 18 8a21.3 21.3 0 0 0 .6 5"/>
      <path d="M17 17H3s3-2 3-9a4.67 4.67 0 0 1 .3-1.7"/>
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
      <line x1="2" x2="22" y1="2" y2="22"/>
    </g>

    <!-- Edit 2 -->
    <g v-else-if="name === 'edit-2'">
      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
    </g>

    <!-- Ticket -->
    <g v-else-if="name === 'ticket'">
      <path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
      <path d="M13 5v2"/>
      <path d="M13 17v2"/>
      <path d="M13 11v2"/>
    </g>

    <!-- Layers -->
    <g v-else-if="name === 'layers'">
      <polygon points="12 2 2 7 12 12 22 7 12 2"/>
      <polyline points="2 17 12 22 22 17"/>
      <polyline points="2 12 12 17 22 12"/>
    </g>

    <!-- More Horizontal -->
    <g v-else-if="name === 'more-horizontal'">
      <circle cx="12" cy="12" r="1"/>
      <circle cx="19" cy="12" r="1"/>
      <circle cx="5" cy="12" r="1"/>
    </g>

    <!-- External Link -->
    <g v-else-if="name === 'external-link'">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" x2="21" y1="14" y2="3"/>
    </g>

    <!-- Shield -->
    <g v-else-if="name === 'shield' || name === 'Shield'">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </g>

    <!-- Wrench / Tool -->
    <g v-else-if="name === 'wrench' || name === 'Wrench' || name === 'tool'">
      <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
    </g>

    <!-- Truck -->
    <g v-else-if="name === 'truck' || name === 'Truck'">
      <rect width="14" height="10" x="1" y="5" rx="1"/>
      <polygon points="15 8 19 8 22 11 22 15 15 15 15 8"/>
      <circle cx="5.5" cy="17.5" r="2.5"/>
      <circle cx="18.5" cy="17.5" r="2.5"/>
    </g>

    <!-- Zap -->
    <g v-else-if="name === 'zap' || name === 'Zap'">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </g>

    <!-- Award -->
    <g v-else-if="name === 'award' || name === 'Award'">
      <circle cx="12" cy="8" r="6"/>
      <path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.2 0l-3.58 2.687a.5.5 0 0 1-.81-.47l1.514-8.526"/>
    </g>

    <!-- FileText -->
    <g v-else-if="name === 'file-text' || name === 'FileText'">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" x2="8" y1="13" y2="13"/>
      <line x1="16" x2="8" y1="17" y2="17"/>
      <line x1="10" x2="8" y1="9" y2="9"/>
    </g>

    <!-- Database -->
    <g v-else-if="name === 'database' || name === 'Database'">
      <ellipse cx="12" cy="5" rx="9" ry="3"/>
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
    </g>

    <!-- Briefcase -->
    <g v-else-if="name === 'briefcase' || name === 'Briefcase'">
      <rect width="20" height="14" x="2" y="7" rx="2" ry="2"/>
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
    </g>

    <!-- Settings / Gear -->
    <g v-else-if="name === 'settings' || name === 'Settings'">
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
      <circle cx="12" cy="12" r="3"/>
    </g>

    <!-- Default fallback -->
    <g v-else>
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" x2="12" y1="8" y2="12"/>
      <line x1="12" x2="12.01" y1="16" y2="16"/>
    </g>
  </svg>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true,
  },
  size: {
    type: [Number, String],
    default: 18,
  },
  color: {
    type: String,
    default: '',
  },
  strokeWidth: {
    type: [Number, String],
    default: 2,
  },
})
</script>

