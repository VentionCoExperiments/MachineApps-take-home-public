import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configurable backend URL - used in Dockerfile
const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    // Same-origin: the browser only ever talks to the Vite dev server, which
    // forwards /rpc to the backend. No cross-origin requests, so no CORS.
    proxy: {
      '/rpc': backendUrl,
    },
  },
})
