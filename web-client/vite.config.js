import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

import packageJson from "./package.json";
import autoprefixer from "autoprefixer";

export default defineConfig({
    plugins: [vue()],
    define: {
        "import.meta.env.VERSION": JSON.stringify(packageJson.version),
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: `@import "@/scss/main.scss";`,
            },
        },
        postcss: {
            plugins: [autoprefixer],
        },
    },
    server: {
        proxy: {
            "/api": "http://localhost:5000",
            "/analytics": "http://localhost:5000"
        },
    }
});
