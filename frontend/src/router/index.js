import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/mentors',
    name: 'Mentors',
    component: () => import('../views/MentorsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/sessions',
    name: 'Sessions',
    component: () => import('../views/SessionsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Global navigation guard for authentication (Vue 3 szabványra javítva)
router.beforeEach((to, from) => {
  // Megnézzük, van-e 'token' elmentve a böngészőben
  const isAuthenticated = !!localStorage.getItem('token')

  // 1. Ha védett oldalra próbál menni, de nincs bejelentkezve -> Login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  } 
  
  // 2. Ha már bejelentkezett, de a Login vagy Register oldalra tévedne -> Dashboard
  if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    return { name: 'Dashboard' }
  } 
  
  // 3. Minden más esetben engedjük tovább az eredeti útvonalra
  return true
})

export default router