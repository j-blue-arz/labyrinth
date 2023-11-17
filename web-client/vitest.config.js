import { mergeConfig, defineConfig } from "vitest/config";

import viteConfig from "./vite.config";

export default mergeConfig(
    viteConfig,
    defineConfig({
        test: {
            environment: "jsdom",
            globals: true,
            setupFiles: ["tests/unit.setup.js"],
        },
    }),
);
