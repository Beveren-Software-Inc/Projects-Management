import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import {
  FrappeUI,
  Button,
  Badge,
  Avatar,
  Dialog,
  Alert,
  TextInput,
  FormControl,
  ErrorMessage,
  Tooltip,
  Dropdown,
  TabButtons,
} from 'frappe-ui'
import { spritePlugin } from 'frappe-ui/experimental'

const globalComponents = {
  Button,
  Badge,
  Avatar,
  Dialog,
  Alert,
  TextInput,
  FormControl,
  ErrorMessage,
  Tooltip,
  Dropdown,
  TabButtons,
}

const pinia = createPinia()
const app = createApp(App)

app.use(FrappeUI)
app.use(spritePlugin)
app.use(pinia)
app.use(router)

for (const key in globalComponents) {
  if (globalComponents[key]) {
    app.component(key, globalComponents[key])
  }
}

app.mount('#app')
