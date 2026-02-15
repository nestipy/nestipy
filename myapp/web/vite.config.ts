import { defineConfig } from 'vite';
import { resolve } from 'node:path';
import react from '@vitejs/plugin-react';
import tailwind from '@tailwindcss/vite';

const backend = process.env.NESTIPY_WEB_PROXY ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react(), tailwind()],
  ssr: {
    noExternal: true,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/_actions': { target: backend, changeOrigin: false },
      '/_router': { target: backend, changeOrigin: false },
      '/_devtools': { target: backend, changeOrigin: false },
      '^/api(/|$)': { target: backend, changeOrigin: false },
    },
    port: 2345,
  },
});