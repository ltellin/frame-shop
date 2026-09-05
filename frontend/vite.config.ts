import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The frontend talks to the backend only through /api, proxied in dev to the
// FastAPI server on :8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
