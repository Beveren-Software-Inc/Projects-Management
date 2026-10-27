import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './pages/Dashboard.vue'
import Projects from './pages/Projects.vue'
import SingleProjectDashboard from './pages/SingleProjectDashboard.vue'
import Tasks from './pages/Tasks.vue'
import Modules from './pages/Modules.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
  },
  {
    path: '/projects/:projectName',
    name: 'SingleProjectDashboard',
    component: SingleProjectDashboard,
    props: true,
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks,
  },
  {
    path: '/tasks/:taskId',
    name: 'TaskDetail',
    component: Tasks,
    props: true,
  },
  {
    path: '/modules',
    name: 'Modules',
    component: Modules,
  },
]

const router = createRouter({
  history: createWebHistory('/projects'),
  routes,
})

export default router

