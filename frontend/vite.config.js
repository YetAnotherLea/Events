import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "My Events",
        short_name: "Events",
        start_url: "/",
        display: "standalone",
      },
      workbox: {
        // Le service worker ne doit pas servir index.html à la place du handler OAuth Firebase ni de l'API
        navigateFallbackDenylist: [/^\/__\//, /^\/api\//],
      },
      devOptions: {
        enabled: true,
        type: "module",
      },
    }),
  ],
  server: {
    host: true,
    port: 5173,
  },
});
