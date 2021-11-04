import { shallowMount } from "@vue/test-utils";
import App from "@/components/App.vue";

let dispatch = jest.fn();

const factory = function() {
    return shallowMount(App, {
        mocks: {
            $store: {
                dispatch: dispatch,
                watch: jest.fn()
            }
        }
    });
};

describe("App", () => {
    it("enters game on startup", () => {
        factory();
        expect(dispatch).toHaveBeenCalledWith("players/enterGame");
    });
});
