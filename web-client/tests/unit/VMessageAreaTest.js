import { mount } from "@vue/test-utils";
import VMessageArea from "@/components/VMessageArea.vue";
import Vue from "vue";
import Player, { NO_ACTION, MOVE_ACTION, SHIFT_ACTION } from "@/model/player.js";

beforeEach(() => {
    wrapper = factory();
});

describe("VMessageBoard", () => {
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

const mockCountdown = {
    remaining: 30,
    startSeconds: 30,
    isRunning: jest.fn().mockReturnValue(true)
};

const player = new Player(0);

const factory = function() {
    let wrapper = mount(VMessageArea, {
        propsData: {
            countdown: mockCountdown,
            userPlayer: player
        }
    });
    return wrapper;
};

const givenNotPlayersTurn = function() {
    player.setTurnAction(NO_ACTION);
};

const givenPlayerShift = function() {
    player.setTurnAction(SHIFT_ACTION);
};

const givenPlayerMove = function() {
    player.setTurnAction(MOVE_ACTION);
};

const whenCountdownReaches = function(seconds) {
    const mockCountdown = {
        remaining: seconds,
        startSeconds: 30,
        isRunning: jest.fn().mockReturnValue(true)
    };
    wrapper.setProps({ countdown: mockCountdown });
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
