/**
 * Хранилище аутентификации (Pinia Store)
 * Отвечает за управление токеном доступа и данными пользователя
 */
import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: null,
  }),
  getters: {
    /**
     * Проверить, авторизован ли пользователь
     */
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    /**
     * Авторизовать пользователя по email и паролю
     * @param {string} email - Email пользователя
     * @param {string} password - Пароль пользователя
     */
    async login(email, password) {
      // FastAPI требует OAuth2PasswordRequestForm (username, password)
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await api.post('/login', formData)
      this.token = response.data.access_token
      localStorage.setItem('access_token', this.token)
      await this.fetchUser()
    },
    /**
     * Получить данные текущего пользователя
     */
    async fetchUser() {
      if (!this.token) return
      try {
        const response = await api.get('/me')
        this.user = response.data
      } catch (error) {
        this.logout()
      }
    },
    /**
     * Выйти из аккаунта (удалить токен и данные)
     */
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    }
  }
})