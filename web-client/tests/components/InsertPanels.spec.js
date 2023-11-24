import { mount } from "@vue/test-utils";
import { createTestingPinia } from "@pinia/testing";
import { createTestStores, GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";
import InsertPanels from "@/components/InsertPanels.vue";
import { SHIFT_ACTION, MOVE_ACTION } from "@/model/player.js";
import { nextTick } from "vue";

beforeEach(() => {
    insertPanels = factory();
});

describe("InsertPanels", () => {
    it("sets interaction class on insert panels if shift is required", async () => {
        givenNoDisabledShiftLocation();
        givenShiftRequired();
        
        await nextTick();

        thenPanelsHaveInteractionClass();
    });

    it("does not set interaction class on insert panels if move is required", async () => {
        givenNoDisabledShiftLocation();
        givenMoveRequired();

        await nextTick();

        thenNoPanelHasInteractionClass();
    });

    it("enables all insert panels but the one which is disabled in game", async () => {
        givenDisabledShiftLocation({ row: 0, column: 1 });
        givenShiftRequired();

        await nextTick();

        thenOnePanelIsDisabled();
        thenDisabledPanelIsTopOfFirstColumn();
    });
});

let insertPanels;
let stores;

const playerId = 1;

const factory = function () {
    let wrapper = mount(InsertPanels, {
        global: {
            plugins: [createTestingPinia({ stubActions: false })],
        },
    });
    stores = createTestStores(GET_GAME_STATE_RESULT_FOR_N_3);
    stores.playersStore.addPlayer({ id: playerId, isUser: true });
    return wrapper;
};

const givenDisabledShiftLocation = function (location) {
    stores.boardStore.setDisabledShiftLocation(location);
};

const givenNoDisabledShiftLocation = function () {
    stores.boardStore.setDisabledShiftLocation(null);
};

const givenShiftRequired = function () {
    stores.gameStore.updateNextAction({ playerId: playerId, action: SHIFT_ACTION });
};

const givenMoveRequired = function () {
    stores.gameStore.updateNextAction({ playerId: playerId, action: MOVE_ACTION });
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
