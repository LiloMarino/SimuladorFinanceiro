import path from "path";
import { copyFileSync, mkdirSync, unlinkSync } from "fs";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig, type Plugin } from "vite";

// Plugin para mover index.html para backend/templates após o build
function moveIndexHtmlPlugin(): Plugin {
  return {
    name: "move-index-html",
    closeBundle() {
      const staticDir = path.resolve(__dirname, "../backend/static");
      const templatesDir = path.resolve(__dirname, "../backend/templates");
      const indexSource = path.join(staticDir, "index.html");
      const indexDest = path.join(templatesDir, "index.html");

      // Cria o diretório templates se não existir
      mkdirSync(templatesDir, { recursive: true });

      // Move index.html para templates
      try {
        copyFileSync(indexSource, indexDest);
        // Remove do static já que foi movido para templates
        unlinkSync(indexSource);
        console.log("✓ index.html movido para backend/templates");
      } catch (error) {
        console.error("✗ Erro ao mover index.html:", error);
      }
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), moveIndexHtmlPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  build: {
    outDir: path.resolve(__dirname, "../backend/static"),
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://localhost:5000", // qualquer /api vai para o Flask
      "/socket.io": {
        target: "http://localhost:5000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
