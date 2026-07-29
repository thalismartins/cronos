import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';

export default defineConfig({
  plugins: [preact({ devToolsEnabled: false })],
  server: {
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
});
