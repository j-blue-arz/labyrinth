import { shallowMount } from "@vue/test-utils";
import App from "@/components/App.vue";

let dispatch = jest.fn();
global.fetch = jest.fn();

const factory = function () {
    return shallowMount(App, {
        mocks: {
            $store: {
                dispatch: dispatch,
                watch: jest.fn(),
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
