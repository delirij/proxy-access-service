/**
 * Хранилище уведомлений (Pinia Store)
 * Отвечает за отображение всплывающих сообщений (success, error, warning и т.д.)
 */
import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    show: false,
    message: '',
    color: 'success'
  }),
  actions: {
    /**
     * Показать сообщение уведомления
     * @param {string} message - Текст сообщения
     * @param {string} color - Цвет (success, error, warning, info)
     */
    showMessage(message, color = 'success') {
      this.message = message
      this.color = color
      this.show = true
    }
  }
})