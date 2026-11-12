import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // Served from the root of Cloud Run (explorer.alejandrocamerlengo.com)
  base: '/',
  plugins: [vue()]
})
