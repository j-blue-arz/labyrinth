import { mount } from "@vue/test-utils";
import VMessageArea from "@/components/VMessageArea.vue";
import { NO_ACTION, MOVE_ACTION, SHIFT_ACTION } from "@/model/player.js";

beforeEach(() => {
    mockStore = createMockStore();
});

describe("VMessageArea", () => {
    it("is invisible if not player's turn", () => {
        givenNotPlayersTurn();

        whenMessageAreaIsCreated();

        thenMessageBoardIsInvisible();
    });

    it("is invisible if score is greater than 0", () => {
        givenPlayerShift();
        givenPlayerScore(1);

        whenMessageAreaIsCreated();

        thenMessageBoardIsInvisible();
    });

    it("shows message if score is 0 and shift is required", async () => {
        givenPlayerShift();
        givenPlayerScore(0);

        whenMessageAreaIsCreated();

        thenMessageBoardIsVisible();
        thenMessageBoardShowsMessageContaining("layout");
    });

    it("shows message if score is 0 and move is required", async () => {
        givenPlayerMove();
        givenPlayerScore(0);

        whenMessageAreaIsCreated();

        thenMessageBoardIsVisible();
        thenMessageBoardShowsMessageContaining("move");
    });
});

let wrapper = null;
let mockStore = null;

const initialPlayer = { id: 0, nextAction: NO_ACTION, score: 0 };

const createMockStore = function () {
    let mockStore = {
        state: {
            countdown: {
                remainingSeconds: 30,
                startSeconds: 30,
            },
        },
        getters: {
            "countdown/isRunning": true,
            "players/userPlayer": { ...initialPlayer },
        },
    };
    return mockStore;
};

const factory = function () {
    let wrapper = mount(VMessageArea, {
        global: {
            mocks: {
                $store: mockStore,
            },
        },
    });
    return wrapper;
};

const givenNotPlayersTurn = function () {
    mockStore.getters["players/userPlayer"].nextAction = NO_ACTION;
};

const givenPlayerShift = function () {
    mockStore.getters["players/userPlayer"].nextAction = SHIFT_ACTION;
};

const givenPlayerMove = function () {
    mockStore.getters["players/userPlayer"].nextAction = MOVE_ACTION;
};

const givenPlayerScore = function (score) {
    mockStore.getters["players/userPlayer"].score = score;
};

const whenMessageAreaIsCreated = function () {
    wrapper = factory();
};

const thenMessageBoardIsInvisible = function () {
    expect(wrapper.find("div").isVisible()).toBe(false);
};

const thenMessageBoardIsVisible = function () {
    expect(wrapper.find("div").isVisible()).toBe(true);
};

const thenMessageBoardShowsMessageContaining = function (text) {
    expect(wrapper.text()).toEqual(expect.stringContaining(text));
};
