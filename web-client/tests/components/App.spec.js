import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "@/components/App.vue";
import { useGameStore } from "@/stores/game.js";
import { createTestingPinia } from "@pinia/testing";
import { shallowMount } from "@vue/test-utils";

global.fetch = vi.fn();

describe("App", () => {
    beforeEach(() => {
        shallowMount(App, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                    }),
                ],
            },
        });
        gameStore = useGameStore();
    });

    it("starts offline game on startup", () => {
        expect(gameStore.playOffline).toHaveBeenCalledTimes(1);
    });
});

let gameStore;
