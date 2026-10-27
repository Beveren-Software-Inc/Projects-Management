import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'

export default defineConfig(() => {
  return {
    plugins: [
      frappeui({
        frappeProxy: true,
        lucideIcons: true,
        jinjaBootData: true,
        codeLanguages: false,
        buildConfig: {
          indexHtmlPath: '../projects/www/projects.html',
          emptyOutDir: true,
          sourcemap: false,
        },
      }),
      vue(),
    ],
    resolve: {
      alias: {
        '@': path.resolve(import.meta.dirname, 'src'),
      },
    },
    build: {
      outDir: '../projects/public/frontend',
      emptyOutDir: true,
      target: 'es2020',
    },
    server: {
      port: 8080,
      proxy: {
        '^/(app|api|assets|files)': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          ws: true,
        },
      },
    },
  }
})
