import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import './style.css'

const localeFiles = import.meta.glob('./content/*.json', { eager: true })
const messages = Object.fromEntries(
  Object.entries(localeFiles).map(([path, mod]) => [
    path.match(/\/([a-z-]+)\.json$/i)[1],
    mod.default
  ])
)

const i18n = createI18n({
  legacy: false,
  locale: 'english',
  fallbackLocale: 'english',
  messages
})

const app = createApp(App)
app.use(i18n)
app.mount('#app')
