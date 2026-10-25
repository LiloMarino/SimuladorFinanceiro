import { existsSync, readFileSync } from "node:fs";
import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { parse } from "smol-toml";
import { defineConfig } from "vite";

const DEFAULT_BACKEND_PORT = 8000;

// O proxy segue a porta de [server] port do config.toml da raiz,
// com 8000 (padrão do backend) quando o arquivo não existe.
function readBackendPort(): number {
  const configPath = path.resolve(import.meta.dirname, "../config.toml");
  if (!existsSync(configPath)) return DEFAULT_BACKEND_PORT;

  const server = parse(readFileSync(configPath, "utf-8")).server;
  const port = typeof server === "object" && server !== null && "port" in server ? server.port : undefined;
  return typeof port === "number" ? port : DEFAULT_BACKEND_PORT;
}

const backendUrl = `http://localhost:${readBackendPort()}`;

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "."),
    },
  },
  build: {
    outDir: path.resolve(import.meta.dirname, "../backend/static"),
    emptyOutDir: true,
  },
  server: {
    forwardConsole: { unhandledErrors: true, logLevels: ["error", "warn"] },
    proxy: {
      "/api": backendUrl,
      "/socket.io": {
        target: backendUrl,
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
