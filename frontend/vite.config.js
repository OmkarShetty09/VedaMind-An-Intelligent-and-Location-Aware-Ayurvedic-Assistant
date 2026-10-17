import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const backend = process.env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Everything the Django backend serves is reachable through this one address (localhost:5173).
    proxy: {
      "/api": { target: backend, changeOrigin: true },
      // Django admin + its static files. Keep the browser's Host header so Django's CSRF origin
      // check sees the same host the admin form was loaded from.
      "/admin": { target: backend, changeOrigin: false },
      "/static": { target: backend, changeOrigin: false },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/tests/setup.js"],
  },
});
