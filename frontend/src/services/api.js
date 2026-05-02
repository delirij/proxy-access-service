/**
 * Сервис API для взаимодействия с бэкенд FastAPI
 * Автоматически добавляет JWT-токен в заголовки запросов
 */
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api', 
})

// Перехватчик запросов: добавить JWT-токен в Authorization заголовок
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Перехватчик ответов: обрабатываем ошибки валидации от FastAPI (код 422)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 422 && Array.isArray(error.response.data.detail)) {
      // Превращаем технический массив ошибок Pydantic в понятную пользователю строку
      const messages = error.response.data.detail.map(err => {
        if (err.loc.includes('password') && err.type === 'string_too_short') return 'Пароль должен содержать минимум 8 символов'
        if (err.loc.includes('email')) return 'Введите корректный email адрес'
        return err.msg // Запасной вариант для остальных ошибок
      })
      error.response.data.detail = messages.join('; ')
    }
    return Promise.reject(error)
  }
)

export default api