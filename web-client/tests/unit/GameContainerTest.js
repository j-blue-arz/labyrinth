import { shallowMount } from "@vue/test-utils";
import GameContainer from "@/components/GameContainer.vue";
import CountdownTimer from "@/model/countdown.js";

const mockCountdownTimer = new CountdownTimer(30);

var mockInitialize = jest.fn();
jest.mock("@/controllers/controller.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            initialize: mockInitialize,
            game: {
                getPlayer: jest.fn().mockReturnValue(null),
                getPlayers: jest.fn().mockReturnValue([]),
                hasStarted: jest.fn().mockReturnValue(true)
            },
            playerManager: {
                getUserPlayerId: jest.fn().mockReturnValue(-1)
            },
            turnCountdown: mockCountdownTimer
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
