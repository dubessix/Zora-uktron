import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuration optimized for local dev with hot reload
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: '127.0.0.1'
  }
})
