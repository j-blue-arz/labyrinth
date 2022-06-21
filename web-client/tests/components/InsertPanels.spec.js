import { mount } from "@vue/test-utils";
import { createTestStore, GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";
import InsertPanels from "@/components/InsertPanels.vue";
import { SHIFT_ACTION, MOVE_ACTION } from "@/model/player.js";

describe("InsertPanels", () => {
    it("sets interaction class on insert panels if shift is required", async () => {
        givenInsertPanels();
        await givenNoDisabledShiftLocation();
        await givenShiftRequired();

        thenPanelsHaveInteractionClass();
    });

    it("does not set interaction class on insert panels if move is required", async () => {
        givenInsertPanels();
        await givenNoDisabledShiftLocation();
        await givenMoveRequired();

        thenNoPanelHasInteractionClass();
    });

    it("enables all insert panels but the one which is disabled in game", async () => {
        givenInsertPanels();
        await givenDisabledShiftLocation({ row: 0, column: 1 });
        await givenShiftRequired();

        thenOnePanelIsDisabled();
        thenDisabledPanelIsTopOfFirstColumn();
    });
});

let insertPanels;
let store;

const playerId = 1;

const factory = function () {
    store = createTestStore(GET_GAME_STATE_RESULT_FOR_N_3);
    store.commit("players/addPlayer", { id: playerId, isUser: true });
    let wrapper = mount(InsertPanels, {
        global: {
            plugins: [store],
        },
    });
    return wrapper;
};

const givenInsertPanels = function () {
    insertPanels = factory();
};

const givenDisabledShiftLocation = function (location) {
    store.commit("board/setDisabledShiftLocation", location);
};

const givenNoDisabledShiftLocation = function () {
    store.commit("board/setDisabledShiftLocation", null);
};

const givenShiftRequired = function () {
    store.commit("game/updateNextAction", { playerId: playerId, action: SHIFT_ACTION });
};

const givenMoveRequired = function () {
    store.commit("game/updateNextAction", { playerId: playerId, action: MOVE_ACTION });
};

function thenDisabledPanelIsTopOfFirstColumn() {
    const insertPanelSVGs = insertPanels.findAll(".insert-panel--disabled");
    let xPos = Number.parseInt(insertPanelSVGs[0].attributes("x"));
    let yPos = Number.parseInt(insertPanelSVGs[0].attributes("y"));
    expect(xPos).toBe(100);
    expect(yPos).toBe(-100);
}

function thenOnePanelIsDisabled() {
    const insertPanelSVGs = insertPanels.findAll(".insert-panel--disabled");
    expect(insertPanelSVGs.length).toBe(1);
}

function thenNoPanelHasInteractionClass() {
    const insertPanelSVGs = insertPanels.findAll(".insert-panel");
    insertPanelSVGs.forEach((panel) => {
        expect(panel.classes("insert-panel--interaction")).toBe(false);
    });
}

function thenPanelsHaveInteractionClass() {
    const insertPanelSVGs = insertPanels.findAll(".insert-panel");
    insertPanelSVGs.forEach((panel) => {
        expect(panel.classes("insert-panel--interaction")).toBe(true);
    });
}
