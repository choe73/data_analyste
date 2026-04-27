import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      { find: '@', replacement: path.resolve(__dirname, '../../frontend/src') },
      { find: '@/components', replacement: path.resolve(__dirname, '../../frontend/src/components') },
      { find: '@/pages', replacement: path.resolve(__dirname, '../../frontend/src/pages') },
      { find: '@/hooks', replacement: path.resolve(__dirname, '../../frontend/src/hooks') },
      { find: '@/lib', replacement: path.resolve(__dirname, '../../frontend/src/lib') },
      { find: '@/types', replacement: path.resolve(__dirname, '../../frontend/src/types') },
    ],
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'],
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
    outDir: '../../frontend/dist',
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
