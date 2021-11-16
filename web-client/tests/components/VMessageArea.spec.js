import { mount } from "@vue/test-utils";
import VMessageArea from "@/components/VMessageArea.vue";
import Vue from "vue";
import { NO_ACTION, MOVE_ACTION, SHIFT_ACTION } from "@/model/player.js";

beforeEach(() => {
    mockStore = createMockStore();
    wrapper = factory();
});

describe("VMessageArea", () => {
    it("is invisible if not player's turn", async () => {
        givenNotPlayersTurn();

        thenMessageBoardIsInvisible();
    });

    it("is invisible if score is greater than 0", () => {
        givenPlayerShift();
        givenPlayerScore(1);

        thenMessageBoardIsInvisible();
    });

    it("shows message if score is 0 and shift is required", () => {
        givenPlayerShift();
        givenPlayerScore(0);

        thenMessageBoardIsVisible();
        thenMessageBoardShowsMessageContaining("layout");
    });

    it("shows message if score is 0 and move is required", () => {
        givenPlayerMove();
        givenPlayerScore(0);

        thenMessageBoardIsVisible();
        thenMessageBoardShowsMessageContaining("move");
    });
});

let wrapper = null;
let mockStore = null;

const initialPlayer = { id: 0, nextAction: NO_ACTION, score: 0 };

const createMockStore = function() {
    let mockStore = {
        state: {
            countdown: {
                remainingSeconds: 30,
                startSeconds: 30
            }
        },
        getters: {
            "countdown/isRunning": true,
            "players/userPlayer": { ...initialPlayer }
        }
    };
    return mockStore;
};

const factory = function() {
    let wrapper = mount(VMessageArea, {
        mocks: {
            $store: mockStore
        }
    });
    return wrapper;
};

const givenNotPlayersTurn = function() {
    mockStore.getters["players/userPlayer"].nextAction = NO_ACTION;
};

const givenPlayerShift = function() {
    mockStore.getters["players/userPlayer"].nextAction = SHIFT_ACTION;
};

const givenPlayerMove = function() {
    mockStore.getters["players/userPlayer"].nextAction = MOVE_ACTION;
};

const givenPlayerScore = function(score) {
    mockStore.getters["players/userPlayer"].score = score;
};

const thenMessageBoardIsInvisible = function() {
    expect(wrapper.find("div").isVisible()).toBe(false);
};

const thenMessageBoardIsVisible = function() {
    expect(wrapper.find("div").isVisible()).toBe(true);
};

const thenMessageBoardShowsMessageContaining = function(text) {
    expect(wrapper.text()).toEqual(expect.stringContaining(text));
};
