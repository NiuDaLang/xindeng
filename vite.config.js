import { defineConfig } from "vite"
import { resolve } from "path"
import tailwindcss from '@tailwindcss/vite'


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
  ],
  // server: {
  //   hmr: false, // Disable HMR
  // },

})
