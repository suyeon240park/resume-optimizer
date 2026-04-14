import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import { copyFileSync, existsSync, rmSync } from "fs";

/**
 * Vite preserves the source-relative path for HTML entries, so
 * src/sidebar/index.html lands at dist/src/sidebar/index.html.
 * Chrome expects it at dist/sidebar/index.html.
 */
function fixSidebarHtmlPath(): Plugin {
  return {
    name: "fix-sidebar-html-path",
    closeBundle() {
      const src = resolve(__dirname, "dist/src/sidebar/index.html");
      const dest = resolve(__dirname, "dist/sidebar/index.html");
      if (existsSync(src)) {
        copyFileSync(src, dest);
        rmSync(resolve(__dirname, "dist/src"), { recursive: true, force: true });
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), fixSidebarHtmlPath()],
  resolve: {
    alias: { "@": resolve(__dirname, "src") },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        sidebar: resolve(__dirname, "src/sidebar/index.html"),
        content: resolve(__dirname, "src/content/index.ts"),
        background: resolve(__dirname, "src/background/index.ts"),
      },
      output: {
        entryFileNames: (chunk) => {
          if (chunk.name === "sidebar") return "sidebar/[name].js";
          return "[name].js";
        },
        chunkFileNames: "sidebar/chunks/[name]-[hash].js",
        assetFileNames: "sidebar/assets/[name]-[hash][extname]",
      },
    },
  },
});
