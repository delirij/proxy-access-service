/**
 * Маршрутизация приложения (Vue Router)
 * Определяет доступные страницы и защиту роутов
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: () => import('../views/LoginView.vue') },
    { path: '/register', component: () => import('../views/RegisterView.vue') },
    { 
      path: '/cabinet', 
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true } 
    }
  ],
})

/**
 * Глобальная защита роутов: если путь требует авторизации, а токена нет → перекидываем на логин
 */
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
