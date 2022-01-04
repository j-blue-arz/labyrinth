import Vuex from "vuex";
import { mount, createLocalVue } from "@vue/test-utils";
import { createStore, GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";
import InsertPanels from "@/components/InsertPanels.vue";
import { SHIFT_ACTION, MOVE_ACTION } from "@/model/player.js";

describe("InsertPanels", () => {
    it("sets interaction class on insert panels if shift is required", () => {
        givenInsertPanels();
        givenNoDisabledShiftLocation();
        givenShiftRequired();

        thenPanelsHaveInteractionClass();
    });

    it("does not set interaction class on insert panels if move is required", () => {
        givenInsertPanels();
        givenNoDisabledShiftLocation();
        givenMoveRequired();

        thenNoPanelHasInteractionClass();
    });

    it("enables all insert panels but the one which is disabled in game", () => {
        givenInsertPanels();
        givenDisabledShiftLocation({ row: 0, column: 1 });
        givenShiftRequired();

        thenOnePanelIsDisabled();
        thenDisabledPanelIsTopOfFirstColumn();
    });
});

let insertPanels;
let store;

const playerId = 1;

const factory = function() {
    const localVue = createLocalVue();
    localVue.use(Vuex);
    store = createStore(GET_GAME_STATE_RESULT_FOR_N_3);
    store.commit("players/addPlayer", { id: playerId, isUser: true });
    let wrapper = mount(InsertPanels, {
        store,
        localVue
    });
    return wrapper;
};

const givenInsertPanels = function() {
    insertPanels = factory();
};

const givenDisabledShiftLocation = function(location) {
    store.commit("board/setDisabledShiftLocation", location);
};

const givenNoDisabledShiftLocation = function() {
    store.commit("board/setDisabledShiftLocation", null);
};

const givenShiftRequired = function() {
    store.commit("game/updateNextAction", { playerId: playerId, action: SHIFT_ACTION });
};

const givenMoveRequired = function() {
    store.commit("game/updateNextAction", { playerId: playerId, action: MOVE_ACTION });
};

function thenDisabledPanelIsTopOfFirstColumn() {
    let insertPanelsHtml = insertPanels.findAll(".insert-panel--disabled");
    let xPos = Number.parseInt(insertPanelsHtml.at(0).attributes("x"));
    let yPos = Number.parseInt(insertPanelsHtml.at(0).attributes("y"));
    expect(xPos).toBe(100);
    expect(yPos).toBe(-100);
}

function thenOnePanelIsDisabled() {
    let insertPanelsHtml = insertPanels.findAll(".insert-panel--disabled");
    expect(insertPanelsHtml.length).toBe(1);
}

function thenNoPanelHasInteractionClass() {
    let insertPanelsHtml = insertPanels.findAll(".insert-panel");
    let insertPanelsWithInteraction = insertPanelsHtml.filter(panel =>
        panel.classes(".insert-panel--interaction")
    );
    expect(insertPanelsWithInteraction.length).toBe(0);
}

function thenPanelsHaveInteractionClass() {
    let insertPanelsHtml = insertPanels.findAll(".insert-panel");
    expect(insertPanelsHtml.is(".insert-panel--interaction")).toBe(true);
}
