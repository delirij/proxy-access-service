import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true })
  ],
  server: {
    host: '0.0.0.0', // Чтобы Vite был доступен извне контейнера (если понадобится запускать dev-режим в docker)
    port: 3000
  }
})