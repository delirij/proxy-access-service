<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Вход в систему</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field v-model="email" label="Email" name="email" prepend-icon="mdi-email" type="email" required></v-text-field>
              <v-text-field v-model="password" label="Пароль" name="password" prepend-icon="mdi-lock" type="password" required></v-text-field>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" type="submit" :loading="loading">Войти</v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center pb-4">
            <router-link to="/register" class="text-decoration-none">Нет аккаунта? Зарегистрируйтесь</router-link>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
/**
 * Страница входа в систему
 * Форма для авторизации пользователя по email и паролю
 */
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const loading = ref(false)
const auth = useAuthStore()
const notification = useNotificationStore()
const router = useRouter()

/**
 * Обработчик входа: отправить данные на сервер и перейти в личный кабинет
 */
const handleLogin = async () => {
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    notification.showMessage('Успешный вход!')
    router.push('/cabinet')
  } catch (error) {
    notification.showMessage(error.response?.data?.detail || 'Неверный логин или пароль', 'error')
  } finally {
    loading.value = false
  }
}
</script>