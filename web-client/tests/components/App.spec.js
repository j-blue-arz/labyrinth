import { shallowMount } from "@vue/test-utils";
import App from "@/components/App.vue";

let dispatch = jest.fn();

const factory = function() {
    return shallowMount(App, {
        mocks: {
            $store: {
                dispatch: dispatch
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
