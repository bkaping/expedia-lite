import { defineConfig } from 'vite'

// The application keeps its small UI template in main.js, so Vue's compiler-enabled
// bundler build is required instead of the runtime-only default.
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      vue: 'vue/dist/vue.esm-bundler.js',
    },
  },
})
