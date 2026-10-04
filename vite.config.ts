import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig} from 'vite';

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true,
          changeOrigin: true,
        },
      },
      watch: {
        ignored: [
          '**/data_store/**',
          '**/models_store/**',
          '**/backend/**',
          '**/*.db',
          '**/*.sqlite*',
          '**/*.db-journal',
          '**/*.db-wal',
          '**/*.csv',
          '**/.tempmediaStorage/**',
          '**/brain/**',
        ],
      },
    },
  };
});
