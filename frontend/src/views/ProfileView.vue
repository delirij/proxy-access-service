<template>
  <v-container class="mt-10">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="elevation-4">
          <v-card-title class="bg-primary text-white d-flex align-center">
            <v-icon class="mr-2">mdi-account-circle</v-icon> Личный кабинет
          </v-card-title>
          <v-card-text class="pt-6" v-if="auth.user">
            <p class="text-h6 mb-2"><strong>Email:</strong> {{ auth.user.email }}</p>
            <p class="mb-4">
              <strong>Статус аккаунта:</strong> 
              <v-chip size="small" :color="auth.user.is_active ? 'success' : 'error'" class="ml-2">
                {{ auth.user.is_active ? 'Активен' : 'Неактивен' }}
              </v-chip>
            </p>

            <p class="mb-4" v-if="auth.user.activation_key">
              <strong>Текущий ключ доступа:</strong> 
              <v-chip size="small" color="info" class="ml-2">{{ auth.user.activation_key }}</v-chip>
            </p>
            <v-divider class="my-4"></v-divider>

            <h3 class="mb-2">Смена пароля</h3>
            <v-form @submit.prevent="updatePassword" class="mb-6">
              <v-row>
                <v-col cols="12" md="6" class="py-0">
                  <v-text-field v-model="newPassword" label="Новый пароль" type="password" required density="compact" variant="outlined"></v-text-field>
                </v-col>
                <v-col cols="12" md="6" class="py-0">
                  <v-text-field v-model="confirmPassword" label="Подтвердите пароль" type="password" required density="compact" variant="outlined"></v-text-field>
                </v-col>
              </v-row>
              <v-btn color="secondary" type="submit" :loading="passwordLoading">Изменить пароль</v-btn>
            </v-form>
            <v-divider class="my-4"></v-divider>

            <h3 class="mb-2">Ключ доступа к прокси</h3>
            <p class="text-body-2 text-grey-darken-1 mb-4">Нажмите кнопку ниже, чтобы сгенерировать новый ключ. Он будет отправлен на вашу электронную почту. Старый ключ при этом перестанет действовать.</p>
            <v-btn color="primary" prepend-icon="mdi-key-variant" @click="updateKey" :loading="loading">Обновить ключ</v-btn>
          </v-card-text>
          <v-card-text v-else class="text-center py-10">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
/**
 * Страница личного кабинета (/cabinet)
 * Отображение текущего ключа доступа, возможность обновить ключ и изменить пароль
 */
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { useNotificationStore } from '../stores/notification'

const auth = useAuthStore()
const notification = useNotificationStore()
const loading = ref(false)
const passwordLoading = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')

/**
 * Загружаем текущего пользователя при монтировании компонента
 */
onMounted(async () => {
  if (!auth.user) {
    await auth.fetchUser()
  }
})

/**
 * Обновить ключ доступа: новый ключ будет отправлен на почту
 * Согласно ТЗ: старый ключ удаляется, генерируется новый
 */
const updateKey = async () => {
  loading.value = true
  try {
    const response = await api.post('/me/update-key')
    auth.user = response.data
    notification.showMessage('Новый ключ отправлен на вашу электронную почту')
  } catch (error) {
    notification.showMessage(error.response?.data?.detail || 'Ошибка при обновлении ключа', 'error')
  } finally {
    loading.value = false
  }
}

/**
 * Обновить пароль пользователя
 * Согласно ТЗ: возможность смены пароля
 */
const updatePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    notification.showMessage('Пароли не совпадают', 'error')
    return
  }
  
  if (newPassword.value.length < 8) {
    notification.showMessage('Пароль должен быть минимум 8 символов', 'error')
    return
  }
  
  passwordLoading.value = true
  try {
    const response = await api.put('/me', { email: auth.user.email, password: newPassword.value })
    auth.user = response.data
    notification.showMessage('Пароль успешно изменен')
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (error) {
    notification.showMessage(error.response?.data?.detail || 'Ошибка при изменении пароля', 'error')
  } finally {
    passwordLoading.value = false
  }
}
</script>