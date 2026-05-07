import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Plugin to copy _redirects file to dist
const copyRedirectsPlugin = {
  name: 'copy-redirects',
  writeBundle() {
    const redirectsContent = '/* /index.html 200\n'
    fs.writeFileSync(path.join(__dirname, 'dist', '_redirects'), redirectsContent)
  }
}

// https://vitejs.dev/config/ - build v2.2
export default defineConfig({
  plugins: [react(), copyRedirectsPlugin],
  resolve: {
    alias: {
      '@/lib/api': path.resolve(__dirname, './src/lib/api.ts'),
      '@/lib/utils': path.resolve(__dirname, './src/lib/utils.ts'),
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['recharts'],
          'ui': ['@radix-ui/react-dialog', '@radix-ui/react-tabs', '@radix-ui/react-toast'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', '@tanstack/react-query'],
  },
})
