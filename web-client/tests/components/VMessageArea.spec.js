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

        whenCountdownReaches(19);
        await Vue.nextTick();

        thenMessageBoardIsInvisible();
    });

    it("is invisible if countdown is greater than 20", () => {
        givenPlayerShift();

        whenCountdownReaches(21);

        thenMessageBoardIsInvisible();
    });

    it("is shows message countdown is less than 20 and shift is required", () => {
        givenPlayerShift();

        whenCountdownReaches(19);

        thenMessageBoardIsVisible();
        thenMessageBoardShowsMessageContaining("layout");
    });

    it("is shows message countdown is less than 20 and move is required", () => {
        givenPlayerMove();

        whenCountdownReaches(19);

        thenMessageBoardIsVisible();
        thenMessageBoardShowsMessageContaining("move");
    });
});

let wrapper = null;
let mockStore = null;

const initialPlayer = { id: 0, nextAction: NO_ACTION };

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

const whenCountdownReaches = function(seconds) {
    mockStore.state.countdown.remainingSeconds = seconds;
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
