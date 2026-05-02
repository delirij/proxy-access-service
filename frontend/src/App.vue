<template>
  <v-app>
    <Navbar />
    <v-main>
      <router-view></router-view>
    </v-main>
    <Notification />
  </v-app>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import Notification from './components/Notification.vue'
import { useAuthStore } from './stores/auth'
import { onMounted } from 'vue'

const auth = useAuthStore()

// При старте приложения проверяем, если есть токен, то стягиваем профиль юзера
onMounted(() => {
  if (auth.token) {
    auth.fetchUser()
  }
})
</script>