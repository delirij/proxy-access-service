<template>
  <v-snackbar v-model="notification.show" :color="notification.color" :timeout="4000" location="top right">
    {{ notification.message }}
    <template v-slot:actions>
      <v-btn variant="text" icon="mdi-close" @click="notification.show = false"></v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import { useNotificationStore } from '../stores/notification'
const notification = useNotificationStore()
</script>