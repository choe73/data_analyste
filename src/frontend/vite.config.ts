// This file redirects to the actual vite config in ../../frontend
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../../frontend/src'),
      '@/components': path.resolve(__dirname, '../../frontend/src/components'),
      '@/pages': path.resolve(__dirname, '../../frontend/src/pages'),
      '@/hooks': path.resolve(__dirname, '../../frontend/src/hooks'),
      '@/lib': path.resolve(__dirname, '../../frontend/src/lib'),
      '@/types': path.resolve(__dirname, '../../frontend/src/types'),
    },
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
