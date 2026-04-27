import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Fix Git case-sensitivity issues on Linux servers
try {
  const libDir = path.resolve(__dirname, 'src/lib')
  if (fs.existsSync(libDir)) {
    const files = fs.readdirSync(libDir)
    const apiFile = files.find(f => f.toLowerCase() === 'api.ts')
    if (apiFile && apiFile !== 'api.ts') {
      fs.renameSync(path.join(libDir, apiFile), path.join(libDir, 'api.ts'))
    }
    const utilsFile = files.find(f => f.toLowerCase() === 'utils.ts')
    if (utilsFile && utilsFile !== 'utils.ts') {
      fs.renameSync(path.join(libDir, utilsFile), path.join(libDir, 'utils.ts'))
    }
  }
} catch (e) {}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
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
          'charts': ['recharts', 'plotly.js', 'react-plotly.js'],
          'ui': ['@radix-ui/react-dialog', '@radix-ui/react-tabs', '@radix-ui/react-toast'],
        },
      },
    },
  },
})
