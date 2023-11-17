import { shallowMount } from "@vue/test-utils";
import App from "@/components/App.vue";

let dispatch = vi.fn();
global.fetch = vi.fn();

const factory = function () {
    return shallowMount(App, {
        global: {
            mocks: {
                $store: {
                    dispatch: dispatch,
                    watch: vi.fn(),
                },
            },
        },
    });
};

describe("App", () => {
    it("starts offline game on startup", () => {
        factory();
        expect(dispatch).toHaveBeenCalledWith("game/playOffline");
    });
});
