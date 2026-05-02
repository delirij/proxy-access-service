/**
 * Точка входа в приложение Vue
 * Инициализирует все плагины: Pinia (состояние), Router (маршрутизация), Vuetify (UI)
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Настройка Vuetify для красивого UI
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  icons: { defaultSet: 'mdi' },
})

const app = createApp(App)

// Подключаем плагины
app.use(createPinia())        // Состояние
app.use(router)               // Маршрутизация
app.use(vuetify)              // UI Vuetify

app.mount('#app')