import { defineConfig } from "vite"
import { resolve } from "path"
import tailwindcss from '@tailwindcss/vite'
import glsl from 'vite-plugin-glsl'


export default defineConfig({
  base: "/static/",
  resolve: {
    alias: {
      "@": resolve("./static"),
    }
  },
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    assetsDir: "django-assets",
    rollupOptions: {
      input: {
        main: resolve("./static/js/main.js"),
      }
    }
  },
  plugins: [
    tailwindcss(),
    glsl(),
  ],
  server: {
    port: 5173,
    strictPort: true,
    origin: 'http://localhost:5173', // Force absolute URLs for HMR
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
    }
  }
})