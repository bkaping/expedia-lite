import { defineConfig } from 'vite'

// The application keeps its small UI template in main.js, so Vue's compiler-enabled
// bundler build is required instead of the runtime-only default.
export default defineConfig({
  resolve: {
    alias: {
      vue: 'vue/dist/vue.esm-bundler.js',
    },
  },
})
