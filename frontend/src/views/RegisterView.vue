<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Регистрация</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field v-model="email" label="Email" name="email" prepend-icon="mdi-email" type="email" required></v-text-field>
              <v-text-field v-model="password" label="Пароль" name="password" prepend-icon="mdi-lock" type="password" required></v-text-field>
              <v-text-field v-model="confirmPassword" label="Подтверждение" name="confirm" prepend-icon="mdi-lock-check" type="password" required></v-text-field>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" type="submit" :loading="loading">Зарегистрироваться</v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center pb-4">
            <router-link to="/login" class="text-decoration-none">Уже есть аккаунт? Войти</router-link>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
/**
 * Страница регистрации
 * Форма для создания нового аккаунта с полем подтверждения пароля
 */
import { ref } from 'vue'
import api from '../services/api'
import { useNotificationStore } from '../stores/notification'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const notification = useNotificationStore()
const router = useRouter()

/**
 * Обработчик регистрации: проверить пароли, отправить данные на сервер
 * Согласно ТЗ: после успешной регистрации показать сообщение о письме с ключом
 */
const handleRegister = async () => {
  if (password.value.length < 8) {
    notification.showMessage('Пароль должен содержать минимум 8 символов', 'error')
    return
  }
  
  if (password.value !== confirmPassword.value) {
    notification.showMessage('Пароли не совпадают', 'error')
    return
  }
  
  loading.value = true
  try {
    await api.post('/register', { 
      email: email.value, 
      password: password.value 
    })
    notification.showMessage('Письмо с ключом отправлено на почту')
    router.push('/login')
  } catch (error) {
    notification.showMessage(error.response?.data?.detail || 'Ошибка регистрации', 'error')
  } finally {
    loading.value = false
  }
}
</script>