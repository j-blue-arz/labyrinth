import { mount } from "@vue/test-utils";
import VMessageArea from "@/components/VMessageArea.vue";
import { NO_ACTION, MOVE_ACTION, SHIFT_ACTION } from "@/model/player.js";
import { createTestingPinia } from "@pinia/testing";
import { usePlayersStore } from "@/stores/players.js";

beforeEach(() => {
    testingPinia = createTestingPinia();
    playersStore = usePlayersStore();
    playersStore.userPlayer = { ...initialPlayer };
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
let playersStore = null;
let testingPinia;

const initialPlayer = { id: 0, nextAction: NO_ACTION, score: 0 };

const givenNotPlayersTurn = function () {
    playersStore.userPlayer.nextAction = NO_ACTION;
};

const givenPlayerShift = function () {
    playersStore.userPlayer.nextAction = SHIFT_ACTION;
};

const givenPlayerMove = function () {
    playersStore.userPlayer.nextAction = MOVE_ACTION;
};

const givenPlayerScore = function (score) {
    playersStore.userPlayer.score = score;
};

const whenMessageAreaIsCreated = function () {
    wrapper = mount(VMessageArea, {
        global: {
            plugins: [testingPinia],
        },
    });
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
