import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/socket.io": {
        target: "http://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
