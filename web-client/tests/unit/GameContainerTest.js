import { shallowMount } from "@vue/test-utils";
import GameContainer from "@/components/GameContainer.vue";

var mockInitialize = jest.fn();
jest.mock("@/controllers/controller.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            initialize: mockInitialize,
            getGame: jest.fn().mockReturnValue({
                getPlayers: jest.fn().mockReturnValue([]),
                hasStarted: jest.fn().mockReturnValue(true)
            })
        };
    });
});

beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    mockInitialize.mockClear();
});

const factory = function() {
    return shallowMount(GameContainer);
};

describe("GameContainer", () => {
    it("Creates and initializes controller on startup", () => {
        factory();
        expect(mockInitialize).toHaveBeenCalled();
    });
});
