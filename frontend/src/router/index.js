import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import { shouldRedirectFromAuthPages, shouldRedirectToLogin } from '../utils/authGuards'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: false } // JAVÍTVA: A Kezdőoldalt is láthatják a vendégek!
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
    meta: { requiresAuth: false } // JAVÍTVA: A Mentorok oldalt is láthatják a vendégek!
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

router.beforeEach((to, from) => {
  const isAuthenticated = !!localStorage.getItem('token')
  const redirectToLogin = shouldRedirectToLogin({
    requiresAuth: !!to.meta.requiresAuth,
    isAuthenticated,
    redirectPath: to.fullPath,
  })
  if (redirectToLogin) {
    return redirectToLogin
  }

  const redirectFromAuthPages = shouldRedirectFromAuthPages({
    routeName: to.name,
    isAuthenticated,
  })
  if (redirectFromAuthPages) {
    return redirectFromAuthPages
  }

  return true
})

export default router