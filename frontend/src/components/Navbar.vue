<template>
  <v-app-bar color="primary" density="compact">
    <v-container class="d-flex align-center py-0">
      <v-app-bar-title>Proxy Access</v-app-bar-title>
      <v-spacer></v-spacer>
      
      <template v-if="auth.isAuthenticated">
        <v-btn to="/cabinet" variant="text" prepend-icon="mdi-account">Кабинет</v-btn>
        <v-btn @click="logout" variant="text" prepend-icon="mdi-logout">Выход</v-btn>
      </template>
      <template v-else>
        <v-btn to="/login" variant="text">Вход</v-btn>
        <v-btn to="/register" variant="text">Регистрация</v-btn>
      </template>
    </v-container>
  </v-app-bar>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>