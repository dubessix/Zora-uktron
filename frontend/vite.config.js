import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuration optimized for local dev with hot reload
// `host: true` binds to 0.0.0.0 and `allowedHosts` permits the sandboxed
// live-preview host so the UI renders in the user's browser.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: true,
    allowedHosts: true,
  },
  preview: {
    host: true,
    allowedHosts: true,
  },
})
