import { shallowMount } from "@vue/test-utils";
import { createTestingPinia } from "@pinia/testing";
import { useGameStore } from "@/stores/game.js";
import App from "@/components/App.vue";
import { beforeEach } from "vitest";

global.fetch = vi.fn();



describe("App", () => {
    beforeEach(() => {
        wrapper = shallowMount(App, {
            global: {
                plugins: [createTestingPinia()],
            },
        });
        gameStore = useGameStore();
    })

    it("starts offline game on startup", () => {
        expect(gameStore.playOffline).toHaveBeenCalledTimes(1);
    });
});

let gameStore;
let wrapper;