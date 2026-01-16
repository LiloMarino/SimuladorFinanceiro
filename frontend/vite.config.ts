import path from "path";
import { copyFileSync, mkdirSync, rmSync, existsSync } from "fs";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig, type Plugin } from "vite";

// Plugin para mover index.html para backend/templates após o build
function moveIndexHtmlPlugin(): Plugin {
  return {
    name: "move-index-html",
    writeBundle() {
      const staticDir = path.resolve(__dirname, "../backend/static");
      const templatesDir = path.resolve(__dirname, "../backend/templates");
      const indexSource = path.join(staticDir, "index.html");
      const indexDest = path.join(templatesDir, "index.html");

      // Cria o diretório templates se não existir
      mkdirSync(templatesDir, { recursive: true });

      // Remove index.html antigo de templates se existir
      if (existsSync(indexDest)) {
        rmSync(indexDest);
      }

      // Move index.html para templates
      try {
        if (!existsSync(indexSource)) {
          throw new Error("index.html não encontrado em backend/static");
        }
        copyFileSync(indexSource, indexDest);
        // Remove do static já que foi movido para templates
        rmSync(indexSource);
        console.log("✓ index.html movido para backend/templates");
      } catch (error) {
        const errorMessage = `Erro ao mover index.html: ${error}`;
        console.error(`✗ ${errorMessage}`);
        throw new Error(errorMessage);
      }
    },
  };
}

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
      "/api": "http://localhost:8000",
      "/socket.io": {
        target: "http://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
