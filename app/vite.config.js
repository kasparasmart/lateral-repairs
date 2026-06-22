import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// App is served from /app on the same host as the marketing site,
// but also works standalone at root. Relative base keeps both working.
export default defineConfig({
  plugins: [react()],
  base: './',
})
